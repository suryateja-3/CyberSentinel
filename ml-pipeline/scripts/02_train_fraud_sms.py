#!/usr/bin/env python3
"""
scripts/02_train_fraud_sms.py
==============================
Train and save a Fraud / SMS Phishing classification model using LSTM.

Algorithm  : Bidirectional LSTM (PyTorch)
Dataset    : UCI SMS Spam Collection
Labels     : ham = LEGITIMATE (0), spam = PHISHING/FRAUD (1)
Output     : models/fraud_lstm_weights.pt
             models/fraud_lstm_tokenizer.joblib
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
import joblib

from utils.data_utils import DATA_RAW, MODELS_DIR, check_min_rows, download_file, ensure_dirs, report_split_info
from utils.metrics_utils import full_report
from utils.dl_models import FraudLSTM
from utils.dl_tokenizers import BasicWordTokenizer
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

DATASET_FILE = DATA_RAW / "SMSSpamCollection"
MODEL_OUT    = MODELS_DIR / "fraud_lstm_weights.pt"
TOKENIZER_OUT = MODELS_DIR / "fraud_lstm_tokenizer.joblib"
DATASET_NAME = "UCI SMS Spam Collection"
CLASS_NAMES  = ["LEGITIMATE", "PHISHING/SPAM"]
UCI_DIRECT_URL = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"

def load_data(seed: int):
    tsv_path = DATA_RAW / "sms_spam.tsv"
    if not DATASET_FILE.exists() and not tsv_path.exists():
        download_file(UCI_DIRECT_URL, tsv_path, "UCI SMS Spam Collection")

    if tsv_path.exists():
        df = pd.read_csv(tsv_path, sep="\t", header=0, names=["label", "message"])
    else:
        df = pd.read_csv(DATASET_FILE, sep="\t", header=None, names=["label", "message"], encoding="latin-1")

    df["label"] = df["label"].str.strip().str.lower()
    df = df[df["label"].isin(["ham", "spam"])]
    df["label_int"] = (df["label"] == "spam").astype(int)
    
    return df["message"].values, df["label_int"].values

def train_model(model, iterator, optimizer, criterion, device):
    epoch_loss = 0
    epoch_acc = 0
    model.train()
    
    for batch in iterator:
        text, text_lengths, labels = batch
        text, text_lengths, labels = text.to(device), text_lengths.to(device), labels.to(device)
        
        optimizer.zero_grad()
        predictions = model(text, text_lengths).squeeze(1)
        loss = criterion(predictions, labels.float())
        
        rounded_preds = torch.round(torch.sigmoid(predictions))
        correct = (rounded_preds == labels).float()
        acc = correct.sum() / len(correct)
        
        loss.backward()
        optimizer.step()
        
        epoch_loss += loss.item()
        epoch_acc += acc.item()
        
    return epoch_loss / len(iterator), epoch_acc / len(iterator)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test-size", type=float, default=0.20)
    parser.add_argument("--epochs", type=int, default=5)
    args = parser.parse_args()

    ensure_dirs()
    device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"  Using device: {device}")

    X, y = load_data(args.seed)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=args.test_size, random_state=args.seed, stratify=y)
    report_split_info(y_train, y_test, {0: "ham (LEGITIMATE)", 1: "spam (PHISHING)"})

    print("[3/6] Tokenizing SMS (Word-level)…")
    tokenizer = BasicWordTokenizer(max_vocab_size=5000, max_len=100)
    tokenizer.build_vocab(X_train)
    
    def process_texts(texts):
        encoded, lengths = [], []
        for t in texts:
            idx, l = tokenizer.encode(t)
            encoded.append(idx)
            lengths.append(l)
        return torch.tensor(encoded, dtype=torch.long), torch.tensor(lengths, dtype=torch.long)

    X_train_seq, X_train_len = process_texts(X_train)
    y_train_seq = torch.tensor(y_train, dtype=torch.float)
    X_test_seq, X_test_len = process_texts(X_test)
    
    train_data = TensorDataset(X_train_seq, X_train_len, y_train_seq)
    train_loader = DataLoader(train_data, batch_size=32, shuffle=True)

    print("\n[4/6] Initialising Bidirectional LSTM Model…")
    model = FraudLSTM(
        vocab_size=tokenizer.vocab_size,
        embed_dim=100,
        hidden_dim=128,
        output_dim=1,
        n_layers=2,
        bidirectional=True,
        dropout=0.3
    )
    model = model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    
    # Handle class imbalance
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    pos_weight = torch.tensor([class_weights[1]/class_weights[0]], dtype=torch.float).to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    print(f"\n[5/6] Training LSTM for {args.epochs} epochs…")
    for epoch in range(args.epochs):
        t0 = time.time()
        train_loss, train_acc = train_model(model, train_loader, optimizer, criterion, device)
        elapsed = time.time() - t0
        print(f"  Epoch {epoch+1:02} | Time: {elapsed:.1f}s | Train Loss: {train_loss:.4f} | Train Acc: {train_acc*100:.2f}%")

    model.eval()
    with torch.no_grad():
        test_preds = torch.sigmoid(model(X_test_seq.to(device), X_test_len.to(device)).squeeze(1)).cpu().numpy()
    
    y_pred = np.round(test_preds).astype(int)
    
    full_report("fraud_lstm", y_test, y_pred, CLASS_NAMES, "Model: Bidirectional LSTM (PyTorch)", args.seed)

    print(f"\n[6/6] Saving PyTorch model and tokenizer to {MODELS_DIR}")
    torch.save(model.state_dict(), MODEL_OUT)
    joblib.dump(tokenizer, TOKENIZER_OUT)
    
    print("\n  ✓ LSTM Training complete!\n")

if __name__ == "__main__":
    main()
