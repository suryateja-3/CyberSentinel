#!/usr/bin/env python3
"""
scripts/01_train_fake_news.py
=============================
Train and save a high-accuracy, de-biased Fake News classification model using DistilBERT.

Dataset    : WELFake (72,134 news articles) + Curated Multi-Domain News (Tech, Business, Science, Health)
Labels     : 0 = REAL, 1 = FAKE
Output     : models/fake_news_model/ (Weights + Config)
             models/fake_news_tokenizer/ (Vocabulary)
Metrics    : reports/fake_news_distilbert_metrics.txt

Improvements:
- De-biases training data by stripping wire-service dateline shortcuts (e.g. 'WASHINGTON (Reuters) -')
- Incorporates domain diversity (Technology, AI, Corporate Governance, Science, Medicine, Public Figures)
- Implements stratified Train (70%) / Validation (15%) / Untouched Test (15%) splits
- Fine-tunes upper transformer layers + classifier while preserving base linguistic representations
- Uses AdamW with linear warmup learning rate schedule and gradient clipping
- Tracks validation loss/macro-F1 after each epoch and saves the best model checkpoint
- Evaluates on untouched held-out test data and runs factual regression tests
"""

import argparse
import sys
import time
import os
from pathlib import Path

# Add ml-pipeline to sys.path
pipeline_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pipeline_dir))

# Ensure Windows terminal/log output never crashes on unicode
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import torch

import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from transformers import (
    DistilBertForSequenceClassification,
    DistilBertTokenizerFast,
    get_linear_schedule_with_warmup
)
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

from utils.data_utils import (
    DATA_RAW,
    MODELS_DIR,
    assert_file_exists,
    ensure_dirs,
    report_split_info,
    clean_wire_datelines,
    format_article_input
)
from utils.metrics_utils import full_report

DATASET_FILE   = DATA_RAW / "WELFake_Dataset.csv"
DIVERSITY_FILE = DATA_RAW / "domain_diversity_news.csv"
MODEL_OUT_DIR  = MODELS_DIR / "fake_news_model"
TOK_OUT_DIR    = MODELS_DIR / "fake_news_tokenizer"
CLASS_NAMES    = ["REAL", "FAKE"]

REGRESSION_SAMPLES = [
    {
        "description": "Factual Executive Biography (Mark Zuckerberg / Meta)",
        "text": "Mark Zuckerberg is famous for co-founding Facebook (now Meta Platforms) and serving as its long-time chief executive officer.",
        "expected": "REAL",
        "expected_id": 0
    },
    {
        "description": "NASA Peer-Reviewed Scientific Discovery",
        "text": "Scientists at NASA confirmed the presence of water ice in permanently shadowed regions near the lunar poles using spectrometer data.",
        "expected": "REAL",
        "expected_id": 0
    },
    {
        "description": "Financial Wire Report (Reuters)",
        "text": "French inflation fell more than expected in September, preliminary EU-harmonised data showed on Friday, supporting bets on further European Central Bank rate cuts.",
        "expected": "REAL",
        "expected_id": 0
    },
    {
        "description": "Conspiracy Clickbait (5G mind control)",
        "text": "EXCLUSIVE: Whistleblowers inside the deep state reveal classified government program using 5G towers to transmit frequency waves that alter human brain chemistry. Share before deleted!",
        "expected": "FAKE",
        "expected_id": 1
    },
    {
        "description": "Miracle Medical Cure Hoax",
        "text": "SHOCKING CURE: Boiled garlic and lemon juice completely eliminates all stage-4 cancerous tumors in 48 hours, but big pharma has suppressed this ancient remedy to protect profits.",
        "expected": "FAKE",
        "expected_id": 1
    }
]

def load_data(seed: int, sample_size: int = 2400):
    print(f"\n[1/6] Loading and de-biasing news datasets...")
    assert_file_exists(DATASET_FILE, "WELFake", "Download from Zenodo / Kaggle")

    # Read WELFake
    df_wf = pd.read_csv(
        DATASET_FILE,
        usecols=lambda c: c.strip().lower() in ["title", "text", "label"],
        low_memory=False
    )
    df_wf.columns = df_wf.columns.str.strip().str.lower()
    df_wf = df_wf.dropna(subset=["label"])
    df_wf["label"] = df_wf["label"].astype(int)
    df_wf["title"] = df_wf["title"].fillna("")
    df_wf["text"]  = df_wf["text"].fillna("")

    # Strip wire datelines from text so model does not exploit shortcuts like '(Reuters) -'
    print("  Removing wire-service dateline shortcuts to prevent spurious lexical correlation...")
    df_wf["cleaned_text"] = df_wf["text"].apply(clean_wire_datelines)

    # Format headline and body consistently
    df_wf["combined"] = [
        format_article_input(t, txt) for t, txt in zip(df_wf["title"], df_wf["cleaned_text"])
    ]

    # Drop short articles (<10 words) and duplicate stories
    df_wf = df_wf[df_wf["combined"].str.split().str.len() >= 10]
    initial_len = len(df_wf)
    df_wf = df_wf.drop_duplicates(subset=["combined"]).reset_index(drop=True)
    print(f"  Deduplicated WELFake corpus: {len(df_wf):,} unique articles retained ({initial_len - len(df_wf):,} duplicates removed).")

    # Draw balanced sample from WELFake
    n_per_class = sample_size // 2
    df_real = df_wf[df_wf["label"] == 0].sample(n=min(n_per_class, (df_wf["label"] == 0).sum()), random_state=seed)
    df_fake = df_wf[df_wf["label"] == 1].sample(n=min(n_per_class, (df_wf["label"] == 1).sum()), random_state=seed)
    df_sampled = pd.concat([df_real, df_fake], ignore_index=True)

    # Incorporate diverse multi-domain news (Technology, AI, Business, Science, Health, Public Figures)
    if DIVERSITY_FILE.exists():
        df_div = pd.read_csv(DIVERSITY_FILE)
        df_div["title"] = df_div["title"].fillna("")
        df_div["text"]  = df_div["text"].fillna("")
        df_div["combined"] = [
            format_article_input(t, txt) for t, txt in zip(df_div["title"], df_div["text"])
        ]
        df_div = df_div[["combined", "label"]].dropna()
        print(f"  Incorporating {len(df_div)} curated multi-domain articles (Tech, Business, Science, Health, Biographies).")
        # Augmented weighting to ensure diverse domains are well-represented
        div_augmented = pd.concat([df_div] * 3, ignore_index=True)
        df_combined = pd.concat([df_sampled[["combined", "label"]], div_augmented], ignore_index=True)
    else:
        df_combined = df_sampled[["combined", "label"]]

    # Ensure no duplicates across entire merged dataset
    df_combined = df_combined.drop_duplicates(subset=["combined"]).sample(frac=1.0, random_state=seed).reset_index(drop=True)
    print(f"  Final curated corpus: {len(df_combined):,} articles (REAL: {(df_combined['label']==0).sum()}, FAKE: {(df_combined['label']==1).sum()})")

    return df_combined["combined"].tolist(), df_combined["label"].tolist()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sample-size", type=int, default=2000, help="WELFake base sample size")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-len", type=int, default=160)
    args = parser.parse_args()

    ensure_dirs()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"  Using device: {device}")

    # Load data
    X, y = load_data(seed=args.seed, sample_size=args.sample_size)

    # Stratified 3-way split: 70% Train, 15% Validation, 15% Untouched Test
    print("\n[2/6] Partitioning stratified splits (70% Train / 15% Validation / 15% Untouched Test)...")
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.15, stratify=y, random_state=args.seed
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.1765, stratify=y_train_val, random_state=args.seed
    )

    report_split_info(y_train, y_test, {0: "REAL", 1: "FAKE"})
    print(f"  Split counts: Train = {len(X_train):,}, Validation = {len(X_val):,}, Untouched Test = {len(X_test):,}")

    print("\n[3/6] Tokenizing with DistilBertTokenizerFast...")
    tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')

    def make_dataset(texts, labels):
        enc = tokenizer(texts, truncation=True, padding=True, max_length=args.max_len, return_tensors='pt')
        return TensorDataset(enc['input_ids'], enc['attention_mask'], torch.tensor(labels, dtype=torch.long))

    train_dataset = make_dataset(X_train, y_train)
    val_dataset   = make_dataset(X_val, y_val)
    test_dataset  = make_dataset(X_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader   = DataLoader(val_dataset, batch_size=32)
    test_loader  = DataLoader(test_dataset, batch_size=32)

    print("\n[4/6] Initialising DistilBertForSequenceClassification...")
    id2label = {0: "REAL", 1: "FAKE"}
    label2id = {"REAL": 0, "FAKE": 1}

    model = DistilBertForSequenceClassification.from_pretrained(
        'distilbert-base-uncased',
        num_labels=2,
        id2label=id2label,
        label2id=label2id
    )

    # Freeze embeddings and lower transformer layers (0, 1, 2)
    # Preserves pre-trained encyclopedic knowledge and accelerates training on CPU
    for param in model.distilbert.embeddings.parameters():
        param.requires_grad = False
    for layer in model.distilbert.transformer.layer[:3]:
        for param in layer.parameters():
            param.requires_grad = False

    model.to(device)

    # Differential learning rates
    classifier_params = list(model.pre_classifier.parameters()) + list(model.classifier.parameters())
    transformer_params = [p for p in model.distilbert.transformer.layer[3:].parameters() if p.requires_grad]

    optimizer = torch.optim.AdamW([
        {'params': transformer_params, 'lr': 2e-5, 'weight_decay': 0.01},
        {'params': classifier_params, 'lr': 1e-4, 'weight_decay': 0.01}
    ])

    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_steps * 0.1),
        num_training_steps=total_steps
    )

    print(f"\n[5/6] Training DistilBERT for {args.epochs} epochs with validation & checkpointing...")
    best_val_f1 = 0.0
    best_state_dict = None
    best_epoch = 1

    for epoch in range(args.epochs):
        model.train()
        train_loss = 0.0
        t0 = time.time()
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids, attention_mask, labels = [b.to(device) for b in batch]
            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()
            train_loss += loss.item()

        elapsed = time.time() - t0
        avg_train_loss = train_loss / len(train_loader)

        # Validation loop
        model.eval()
        val_preds, val_targets = [], []
        val_loss = 0.0
        with torch.no_grad():
            for batch in val_loader:
                input_ids, attention_mask, labels = [b.to(device) for b in batch]
                outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
                val_loss += outputs.loss.item()
                preds = torch.argmax(outputs.logits, dim=-1)
                val_preds.extend(preds.cpu().numpy())
                val_targets.extend(labels.cpu().numpy())

        avg_val_loss = val_loss / len(val_loader)
        val_acc = accuracy_score(val_targets, val_preds)
        val_f1  = f1_score(val_targets, val_preds, average='macro')

        print(
            f"  Epoch {epoch+1:02}/{args.epochs:02} | Time: {elapsed:.1f}s | "
            f"Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} | "
            f"Val Acc: {val_acc*100:.2f}% | Val Macro F1: {val_f1*100:.2f}%"
        )

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_epoch = epoch + 1
            best_state_dict = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    # Load best checkpoint before final test evaluation
    if best_state_dict:
        model.load_state_dict(best_state_dict)
        print(f"  [OK] Restored best model weights from Epoch {best_epoch:02} (Val Macro F1: {best_val_f1*100:.2f}%)")

    # Final evaluation on untouched test set
    print("\n  Evaluating on UNTOUCHED held-out test set...")
    model.eval()
    test_preds = []
    with torch.no_grad():
        for batch in test_loader:
            input_ids, attention_mask, _ = [b.to(device) for b in batch]
            outputs = model(input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs.logits, dim=-1)
            test_preds.extend(preds.cpu().numpy())

    extra_notes = (
        f"Algorithm: DistilBERT (Fine-Tuned with De-Biasing & Domain Diversity)\n"
        f"Epochs: {args.epochs} (Best Epoch: {best_epoch})\n"
        f"Validation Macro F1: {best_val_f1*100:.2f}%\n"
        f"Untouched Test Set Size: {len(y_test):,} articles"
    )
    full_report("fake_news_distilbert", y_test, test_preds, CLASS_NAMES, extra_notes, args.seed)

    # Regression testing on key cases
    print("\n  Running regression test suite...")
    all_passed = True
    for item in REGRESSION_SAMPLES:
        enc = tokenizer(item["text"], return_tensors='pt', truncation=True, padding=True, max_length=args.max_len)
        enc = {k: v.to(device) for k, v in enc.items()}
        with torch.no_grad():
            out = model(**enc)
            probs = torch.softmax(out.logits, dim=-1)[0].cpu().numpy()
            pred_id = int(np.argmax(probs))
            pred_label = id2label[pred_id]

        is_match = (pred_id == item["expected_id"])
        if not is_match:
            all_passed = False
        symbol = "[PASS]" if is_match else "[FAIL]"
        prob_real = probs[0] * 100
        prob_fake = probs[1] * 100
        print(f"    {symbol} {item['description']}")
        print(f"        Input     : \"{item['text'][:85]}...\"")
        print(f"        Predicted : {pred_label} (Real: {prob_real:.1f}%, Fake: {prob_fake:.1f}%) | Expected: {item['expected']}")

    if all_passed:
        print("\n  [OK] All regression tests passed successfully!")
    else:
        print("\n  [WARN] Some regression tests did not match expected values.")

    # Save PyTorch model and tokenizer
    print(f"\n[6/6] Saving best model and tokenizer to:\n  - {MODEL_OUT_DIR}\n  - {TOK_OUT_DIR}")
    model.save_pretrained(MODEL_OUT_DIR)
    tokenizer.save_pretrained(TOK_OUT_DIR)
    print("\n  [OK] DistilBERT Training & Export complete!\n")

if __name__ == "__main__":
    main()
