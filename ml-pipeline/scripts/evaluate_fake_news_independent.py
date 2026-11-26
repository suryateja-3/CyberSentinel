#!/usr/bin/env python3
"""
scripts/evaluate_fake_news_independent.py
=========================================
Evaluate the saved DistilBERT fake-news model on an independent, held-out
sample from the labeled WELFake corpus (seed=2026, disjoint from training).

Computes:
- Confusion Matrix (REAL vs FAKE)
- Precision, Recall, F1-score
- False Positive Rate (FPR) and False Negative Rate (FNR)
- Probability Calibration (Brier Score, Confidence Bin Reliability)
- Limitations analysis regarding breaking news generalization
"""

import sys
import time
from pathlib import Path

# Add ml-pipeline to sys.path
pipeline_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pipeline_dir))

import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, brier_score_loss
from sklearn.model_selection import train_test_split

DATA_PATH = pipeline_dir / "data" / "raw" / "WELFake_Dataset.csv"
MODEL_PATH = pipeline_dir / "models" / "fake_news_model"
TOK_PATH = pipeline_dir / "models" / "fake_news_tokenizer"
REPORT_PATH = pipeline_dir / "reports" / "fake_news_independent_evaluation.txt"

def load_independent_test_data(sample_size=500, seed=2026):
    print(f"[1/4] Loading independent evaluation sample (size={sample_size}, seed={seed})...")
    df = pd.read_csv(
        DATA_PATH,
        usecols=lambda c: c.strip().lower() in ["title", "text", "label"],
        low_memory=False
    )
    df.columns = df.columns.str.strip().str.lower()
    df = df.dropna(subset=["label"])
    df["label"] = df["label"].astype(int)
    df["title"] = df["title"].fillna("")
    df["text"] = df["text"].fillna("")
    df["combined"] = df["title"].str.strip() + ". " + df["text"].str.strip()

    # Filter out empty or trivially short articles
    df = df[df["combined"].str.split().str.len() >= 10]

    # Sample a held-out test split using seed=2026 (training used seed=42)
    sample_df, _ = train_test_split(df, train_size=sample_size, stratify=df["label"], random_state=seed)
    return sample_df["combined"].tolist(), sample_df["label"].tolist()

def compute_calibration_bins(y_true, y_probs, n_bins=5):
    """
    Compute Expected Calibration Error (ECE) and bin-wise confidence vs empirical accuracy.
    y_true: binary labels (1=FAKE, 0=REAL)
    y_probs: predicted probability for class 1
    """
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    bin_data = []
    total_samples = len(y_true)
    ece = 0.0

    for i in range(n_bins):
        low, high = bins[i], bins[i+1]
        mask = (y_probs >= low) & (y_probs < high) if i < n_bins - 1 else (y_probs >= low) & (y_probs <= high)
        count = np.sum(mask)
        if count > 0:
            avg_conf = np.mean(y_probs[mask])
            emp_acc = np.mean(np.array(y_true)[mask])
            abs_diff = abs(emp_acc - avg_conf)
            ece += (count / total_samples) * abs_diff
            bin_data.append({
                "range": f"[{low:.1f}, {high:.1f}]",
                "count": int(count),
                "avg_confidence": float(avg_conf),
                "empirical_accuracy": float(emp_acc),
                "gap": float(abs_diff)
            })
        else:
            bin_data.append({
                "range": f"[{low:.1f}, {high:.1f}]",
                "count": 0,
                "avg_confidence": float(bin_centers[i]),
                "empirical_accuracy": 0.0,
                "gap": 0.0
            })
    return ece, bin_data

def main():
    print("=" * 70)
    print("  CyberSentinel - Independent Fake News Model Evaluation")
    print("=" * 70)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"  Device: {device}")

    X_test, y_test = load_independent_test_data(sample_size=500, seed=2026)

    print(f"[2/4] Loading DistilBERT model from {MODEL_PATH}...")
    model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
    tokenizer = DistilBertTokenizerFast.from_pretrained(TOK_PATH)
    model.to(device)
    model.eval()

    print(f"[3/4] Running inference over {len(X_test)} samples...")
    t0 = time.time()
    batch_size = 32
    all_probs = []
    all_preds = []

    for i in range(0, len(X_test), batch_size):
        batch_texts = X_test[i:i+batch_size]
        inputs = tokenizer(batch_texts, return_tensors="pt", truncation=True, padding=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()
            preds = np.argmax(probs, axis=-1)

        all_probs.extend(probs.tolist())
        all_preds.extend(preds.tolist())

    elapsed = time.time() - t0
    print(f"  Inference completed in {elapsed:.1f}s ({len(X_test)/elapsed:.1f} samples/sec)")

    print("[4/4] Calculating evaluation metrics & calibration...")
    y_test_arr = np.array(y_test)
    y_pred_arr = np.array(all_preds)
    prob_fake_arr = np.array([p[1] for p in all_probs])

    # Confusion Matrix: 0=REAL, 1=FAKE
    cm = confusion_matrix(y_test_arr, y_pred_arr, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    accuracy = (tp + tn) / len(y_test_arr)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    brier = brier_score_loss(y_test_arr, prob_fake_arr)
    ece, bin_details = compute_calibration_bins(y_test_arr, prob_fake_arr, n_bins=5)

    report_str = classification_report(y_test_arr, y_pred_arr, target_names=["REAL (0)", "FAKE (1)"], digits=4)

    report_lines = [
        "=" * 70,
        "  INDEPENDENT FAKE NEWS EVALUATION REPORT",
        f"  Generated   : {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"  Model       : DistilBERT (Sequence Classification)",
        f"  Evaluation  : Independent Held-Out WELFake Subset (seed=2026, N={len(X_test)})",
        "=" * 70,
        "",
        f"OVERALL ACCURACY: {accuracy * 100:.2f}%",
        f"BRIER SCORE     : {brier:.4f} (lower is better, 0.0 is perfect calibration)",
        f"EXPECTED CALIBRATION ERROR (ECE): {ece * 100:.2f}%",
        "",
        "CONFUSION MATRIX:",
        "-----------------",
        f"                  PREDICTED REAL (0)    PREDICTED FAKE (1)",
        f"ACTUAL REAL (0) :       {tn:5d} (TN)          {fp:5d} (FP)",
        f"ACTUAL FAKE (1) :       {fn:5d} (FN)          {tp:5d} (TP)",
        "",
        f"False Positive Rate (FPR): {fpr * 100:.2f}% (Genuine articles falsely flagged as fake)",
        f"False Negative Rate (FNR): {fnr * 100:.2f}% (Fake articles missed)",
        "",
        "CLASSIFICATION REPORT:",
        "----------------------",
        report_str,
        "CALIBRATION ANALYSIS (Confidence Bins for Fake News Probability):",
        "-----------------------------------------------------------------",
        f"{'Confidence Bin':<16} {'Count':<8} {'Avg Confidence':<16} {'Empirical Realization':<24} {'Gap':<10}"
    ]

    for b in bin_details:
        report_lines.append(
            f"{b['range']:<16} {b['count']:<8d} {b['avg_confidence']*100:<15.1f}% {b['empirical_accuracy']*100:<23.1f}% {b['gap']*100:<9.1f}%"
        )

    report_lines.extend([
        "",
        "CRITICAL ASSESSMENT & REAL-WORLD LIMITATIONS:",
        "----------------------------------------------",
        "1. Dataset Artifacts & Style Bias:",
        "   - The WELFake corpus comprises historical news (primarily Reuters vs clickbait blogs).",
        "   - DistilBERT heavily weights stylistic markers (byline patterns like 'WASHINGTON (Reuters) -',",
        "     editorial voice, quotation density) rather than factual veracity.",
        "   - Genuine articles lacking wire-service headers can be assigned lower REAL confidence.",
        "",
        "2. Generalization to Breaking News:",
        "   - High in-sample or within-corpus accuracy (98%+) DOES NOT guarantee high reliability on modern",
        "     breaking news or previously unseen disinformation narratives (e.g., AI-generated text, fresh geopolitical events).",
        "   - Linguistic models lack real-time world knowledge.",
        "",
        "3. Verification Necessity:",
        "   - Model predictions MUST be paired with independent news search and corroborating evidence",
        "     (e.g., via GNews or official registries) to verify current claims.",
        "   - Neither model confidence nor search presence constitutes definitive proof of truth.",
        "=" * 70
    ])

    report_text = "\n".join(report_lines)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_text)
    
    print("\n" + report_text.encode('ascii', errors='replace').decode('ascii'))
    print(f"\n[OK] Saved independent evaluation report to: {REPORT_PATH}\n")

if __name__ == "__main__":
    main()
