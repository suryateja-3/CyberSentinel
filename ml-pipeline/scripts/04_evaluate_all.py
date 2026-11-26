#!/usr/bin/env python3
"""
scripts/04_evaluate_all.py
==========================
Load all three saved PyTorch deep learning models (DistilBERT Fake News, Fraud LSTM, URL CNN)
and run sanity checks and regression tests to verify that the models load correctly
and produce accurate, sensible predictions.

Usage:
    python scripts/04_evaluate_all.py
"""

from __future__ import annotations

import sys
import re
from pathlib import Path

pipeline_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pipeline_dir))

# Ensure Windows terminal/log output never crashes on unicode
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import torch

import numpy as np
import joblib
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast

from utils.data_utils import MODELS_DIR, format_article_input
from utils.dl_models import FraudLSTM, URLCharCNN

device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')

# ---------------------------------------------------------------------------
# Test Suites
# ---------------------------------------------------------------------------

FAKE_NEWS_TESTS = [
    {
        "category": "Factual Executive Biography (Mark Zuckerberg)",
        "expected": "REAL",
        "expected_id": 0,
        "text": "Mark Zuckerberg is famous for co-founding Facebook (now Meta Platforms) and serving as its long-time chief executive officer.",
    },
    {
        "category": "Peer-Reviewed Science (NASA Moon Ice)",
        "expected": "REAL",
        "expected_id": 0,
        "text": (
            "Scientists at NASA have confirmed the presence of water ice near "
            "the lunar south pole, according to a peer-reviewed study published "
            "in Nature Geoscience. The discovery was made using data from the "
            "Lunar Reconnaissance Orbiter and corroborated by two independent research groups."
        ),
    },
    {
        "category": "Wire Financial Report (Reuters)",
        "expected": "REAL",
        "expected_id": 0,
        "text": (
            "PARIS - French inflation fell more than expected in September, "
            "preliminary EU-harmonised data showed on Friday, supporting bets on further "
            "European Central Bank rate cuts. Consumer prices in the euro zone's second-biggest "
            "economy rose 1.5% year-on-year."
        ),
    },
    {
        "category": "Federal Reserve Monetary Policy",
        "expected": "REAL",
        "expected_id": 0,
        "text": (
            "The Federal Reserve raised interest rates by 25 basis points on "
            "Wednesday, as policymakers continue efforts to bring inflation down "
            "toward the 2% target. Fed Chair Jerome Powell said policymakers remain committed to price stability."
        ),
    },
    {
        "category": "Conspiracy Clickbait (5G mind control)",
        "expected": "FAKE",
        "expected_id": 1,
        "text": (
            "EXCLUSIVE!! Deep state whistleblower reveals that 5G towers are secretly "
            "broadcasting frequency waves that alter human brain chemistry and control thoughts. "
            "The mainstream media is covering this up!! Share before it gets deleted! Anonymous sources confirm."
        ),
    },
    {
        "category": "Miracle Medical Cure Hoax",
        "expected": "FAKE",
        "expected_id": 1,
        "text": (
            "SHOCKING CURE: Boiled garlic cloves and raw lemon juice completely cures all "
            "cancers in 48 hours without chemotherapy. Big Pharma executives paid billions to bury "
            "this miracle home remedy from medical journals to protect profits. Share to save lives!"
        ),
    },
    {
        "category": "Fabricated Corporate Android Hoax",
        "expected": "FAKE",
        "expected_id": 1,
        "text": (
            "LEAKED FOOTAGE: Anonymous engineers claim Mark Zuckerberg was replaced by a "
            "synthetic humanoid robot in 2019. Whistleblowers leaked classified documents showing "
            "the real billionaire has been detained in a secret underground military bunker."
        ),
    }
]

SMS_FRAUD_TESTS = [
    {
        "category": "Legitimate Personal Chat",
        "expected": "LEGITIMATE",
        "expected_id": 0,
        "text": "Hey, are we still meeting for lunch at 1pm? Let me know!",
    },
    {
        "category": "Legitimate Shipping Notice",
        "expected": "LEGITIMATE",
        "expected_id": 0,
        "text": "Your Amazon order #112-8374920 has been shipped and will be delivered by Friday.",
    },
    {
        "category": "Phishing Banking Alert",
        "expected": "PHISHING/SPAM",
        "expected_id": 1,
        "text": (
            "URGENT: Your bank account has been suspended! "
            "Click here NOW to verify your details and avoid permanent closure: "
            "http://secure-bank-verify.xyz/login?id=839472"
        ),
    },
    {
        "category": "Lottery Scam",
        "expected": "PHISHING/SPAM",
        "expected_id": 1,
        "text": "Congratulations! You've been selected as a WINNER in our weekly draw. Claim your FREE £500 gift card now. Reply WIN to 88989.",
    },
]

URL_TESTS = [
    {
        "category": "Benign Developer Repo",
        "expected": "BENIGN",
        "expected_id": 0,
        "url": "https://github.com/scikit-learn/scikit-learn",
    },
    {
        "category": "Benign Major News Domain",
        "expected": "BENIGN",
        "expected_id": 0,
        "url": "https://www.bbc.com/news/technology-58476775",
    },
    {
        "category": "Benign Official Financial Domain",
        "expected": "BENIGN",
        "expected_id": 0,
        "url": "https://www.rbi.org.in",
    },
    {
        "category": "Malicious Phishing Portal (PayPal typo)",
        "expected": "MALICIOUS",
        "expected_id": 1,
        "url": "http://paypa1-secure-account-verify.ru/login?token=abc123xyz",
    },
    {
        "category": "Malicious IP-based Phishing",
        "expected": "MALICIOUS",
        "expected_id": 1,
        "url": "http://192.168.1.104/wp-admin/free-iphone",
    },
    {
        "category": "Malicious Redirect Phishing",
        "expected": "MALICIOUS",
        "expected_id": 1,
        "url": "http://bit.ly/3xR9zQ2?redirect=bankofamerica.phish-login.net",
    },
]

def evaluate_fake_news():
    print("\n" + "=" * 70)
    print("  1. FAKE NEWS CLASSIFIER (DistilBERT)")
    print("=" * 70)

    model_dir = MODELS_DIR / "fake_news_model"
    tok_dir = MODELS_DIR / "fake_news_tokenizer"

    if not model_dir.exists() or not tok_dir.exists():
        print(f"  [SKIP] Model artifacts not found at {model_dir}")
        print("  Run: python scripts/01_train_fake_news.py")
        return False

    model = DistilBertForSequenceClassification.from_pretrained(model_dir, local_files_only=True)
    tokenizer = DistilBertTokenizerFast.from_pretrained(tok_dir, local_files_only=True)
    model.to(device)
    model.eval()

    all_passed = True
    for i, test in enumerate(FAKE_NEWS_TESTS):
        inputs = tokenizer(test["text"], return_tensors="pt", truncation=True, padding=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0].cpu().numpy()
            pred_id = int(np.argmax(probs))

        pred_label = "REAL" if pred_id == 0 else "FAKE"
        prob_real = probs[0] * 100
        prob_fake = probs[1] * 100
        is_match = (pred_label == test["expected"])
        if not is_match:
            all_passed = False
        symbol = "[PASS]" if is_match else "[FAIL]"

        excerpt = test["text"][:75].replace("\n", " ") + ("…" if len(test["text"]) > 75 else "")
        print(f"\n  [{i+1}] {test['category']}")
        print(f"       Input    : \"{excerpt}\"")
        print(f"       Logits   : [{outputs.logits[0][0]:.3f}, {outputs.logits[0][1]:.3f}]")
        print(f"       Scores   : Real: {prob_real:.1f}%, Fake: {prob_fake:.1f}%")
        print(f"       Verdict  : {pred_label}  {symbol} (Expected: {test['expected']})")

    return all_passed

def evaluate_sms_fraud():
    print("\n" + "=" * 70)
    print("  2. FRAUD / SMS PHISHING CLASSIFIER (Bidirectional LSTM)")
    print("=" * 70)

    model_path = MODELS_DIR / "fraud_lstm_weights.pt"
    tok_path = MODELS_DIR / "fraud_lstm_tokenizer.joblib"

    if not model_path.exists() or not tok_path.exists():
        print(f"  [SKIP] Model artifacts not found at {model_path}")
        return False

    tokenizer = joblib.load(tok_path)
    model = FraudLSTM(
        vocab_size=tokenizer.vocab_size,
        embed_dim=100, hidden_dim=128, output_dim=1,
        n_layers=2, bidirectional=True, dropout=0.3
    )
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    model.to(device)
    model.eval()

    all_passed = True
    for i, test in enumerate(SMS_FRAUD_TESTS):
        seq, seq_len = tokenizer.encode(test["text"])
        seq_t = torch.tensor([seq], dtype=torch.long).to(device)
        len_t = torch.tensor([seq_len], dtype=torch.long).to(device)

        with torch.no_grad():
            logits = model(seq_t, len_t).squeeze(1)
            prob = torch.sigmoid(logits)[0].item()

        pred_label = "PHISHING/SPAM" if prob > 0.5 else "LEGITIMATE"
        conf = prob if prob > 0.5 else (1.0 - prob)
        is_match = (pred_label == test["expected"])
        if not is_match:
            all_passed = False
        symbol = "[PASS]" if is_match else "[FAIL]"

        excerpt = test["text"][:75].replace("\n", " ") + ("…" if len(test["text"]) > 75 else "")
        print(f"\n  [{i+1}] {test['category']}")
        print(f"       Input    : \"{excerpt}\"")
        print(f"       Predicted: {pred_label} ({conf*100:.1f}% confidence)  {symbol}")

    return all_passed

def evaluate_url_cnn():
    print("\n" + "=" * 70)
    print("  3. MALICIOUS URL DETECTOR (1D Char CNN)")
    print("=" * 70)

    model_path = MODELS_DIR / "url_cnn_weights.pt"
    tok_path = MODELS_DIR / "url_cnn_tokenizer.joblib"

    if not model_path.exists() or not tok_path.exists():
        print(f"  [SKIP] Model artifacts not found at {model_path}")
        return False

    tokenizer = joblib.load(tok_path)
    model = URLCharCNN(
        vocab_size=tokenizer.vocab_size,
        embed_dim=64, n_filters=100, filter_sizes=[3, 4, 5], output_dim=1, dropout=0.5
    )
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    model.to(device)
    model.eval()

    all_passed = True
    for i, test in enumerate(URL_TESTS):
        raw_u = test["url"].lower().strip()
        cleaned = re.sub(r'^https?://', '', raw_u)
        cleaned = re.sub(r'^www\.', '', cleaned)

        seq = tokenizer.encode(cleaned)
        seq_t = torch.tensor([seq], dtype=torch.long).to(device)

        with torch.no_grad():
            logits = model(seq_t).squeeze(1)
            prob = torch.sigmoid(logits)[0].item()

        pred_label = "MALICIOUS" if prob > 0.5 else "BENIGN"
        conf = prob if prob > 0.5 else (1.0 - prob)
        is_match = (pred_label == test["expected"])
        if not is_match:
            all_passed = False
        symbol = "[PASS]" if is_match else "[FAIL]"

        print(f"\n  [{i+1}] {test['category']}")
        print(f"       URL      : {test['url']}")
        print(f"       Predicted: {pred_label} ({conf*100:.1f}% confidence)  {symbol}")

    return all_passed

def main():
    print("=" * 70)
    print("  CyberSentinel — PyTorch Deep Learning Models Sanity & Regression Check")
    print(f"  Device: {device}")
    print("=" * 70)

    fn_ok = evaluate_fake_news()
    sms_ok = evaluate_sms_fraud()
    url_ok = evaluate_url_cnn()

    print("\n" + "=" * 70)
    print("  SUMMARY REPORT")
    print("=" * 70)
    print(f"  Fake News Classifier (DistilBERT) : {'PASSED [OK]' if fn_ok else 'FAILED [MISMATCH]'}")
    print(f"  Fraud SMS Classifier (LSTM)       : {'PASSED [OK]' if sms_ok else 'FAILED [MISMATCH]'}")
    print(f"  Malicious URL Classifier (CNN)    : {'PASSED [OK]' if url_ok else 'FAILED [MISMATCH]'}")
    print("=" * 70 + "\n")

    if not (fn_ok and sms_ok and url_ok):
        sys.exit(1)

if __name__ == "__main__":
    main()
