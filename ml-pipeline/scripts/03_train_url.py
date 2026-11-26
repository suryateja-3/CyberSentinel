#!/usr/bin/env python3
"""
scripts/03_train_url.py
=======================
Train and save a Malicious URL 1D CNN model (PyTorch).

Algorithm  : 1D CNN (Character-level)
Dataset    : Malicious URLs Dataset (Kaggle: sid321axn/malicious-urls-dataset)
Labels     : benign = 0, malicious = 1
Output     : models/url_cnn_weights.pt
             models/url_cnn_tokenizer.joblib
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

from utils.data_utils import DATA_RAW, MODELS_DIR, assert_file_exists, check_min_rows, ensure_dirs, report_split_info
from utils.metrics_utils import full_report
from utils.dl_models import URLCharCNN
from utils.dl_tokenizers import CharTokenizer
from sklearn.model_selection import train_test_split

DATASET_FILE = DATA_RAW / "malicious_phish.csv"
MODEL_OUT    = MODELS_DIR / "url_cnn_weights.pt"
TOKENIZER_OUT = MODELS_DIR / "url_cnn_tokenizer.joblib"
DATASET_NAME = "Malicious URLs Dataset (Kaggle sid321axn)"
CLASS_NAMES  = ["BENIGN", "MALICIOUS"]

def load_data(seed: int, sample_size: int):
    print(f"\n[1/6] Loading dataset: {DATASET_NAME}")
    assert_file_exists(DATASET_FILE, DATASET_NAME, "Download from Kaggle")
    
    header = pd.read_csv(DATASET_FILE, nrows=0).columns.tolist()
    
    cols_to_use = ["url"]
    target_col = None
    if "type" in header:
        cols_to_use.append("type")
        target_col = "type"
    elif "label" in header:
        cols_to_use.append("label")
        target_col = "label"
    else:
        raise ValueError(f"Dataset missing target column. Found columns: {header}")
        
    import re
    def clean_url(u):
        u = str(u).lower().strip()
        u = re.sub(r'^https?://', '', u)
        u = re.sub(r'^www\.', '', u)
        return u

    df = pd.read_csv(DATASET_FILE, usecols=cols_to_use, low_memory=False)
    df = df.dropna(subset=cols_to_use)
    df["url"] = df["url"].apply(clean_url)
    
    if target_col == "type":
        df["type"] = df["type"].astype(str).str.strip().str.lower()
        known = {"benign", "phishing", "defacement", "malware"}
        unknown = set(df["type"].unique()) - known
        if unknown:
            print(f"Warning: Found unknown labels in 'type' column: {unknown}")
        
        df["label"] = (df["type"] != "benign").astype(int)
    else:
        df["label"] = df["label"].astype(int)

    if sample_size and sample_size < len(df):
        print(f"  Sampling {sample_size:,} rows for faster training…")
        from sklearn.model_selection import train_test_split
        _, df = train_test_split(df, test_size=sample_size, random_state=seed, stratify=df["label"])
        df = df.reset_index(drop=True)

    return df["url"].values, df["label"].values

def train_model(model, iterator, optimizer, criterion, device):
    epoch_loss = 0
    epoch_acc = 0
    model.train()
    
    for batch in iterator:
        text, labels = batch
        text, labels = text.to(device), labels.to(device)
        
        optimizer.zero_grad()
        predictions = model(text).squeeze(1)
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
    parser.add_argument("--sample-size", type=int, default=50_000, help="Subset for CNN")
    parser.add_argument("--epochs", type=int, default=3)
    args = parser.parse_args()

    ensure_dirs()
    device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"  Using device: {device}")

    X, y = load_data(args.seed, args.sample_size)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=args.test_size, random_state=args.seed, stratify=y)
    report_split_info(y_train, y_test, {0: "BENIGN", 1: "MALICIOUS"})

    print("[3/6] Tokenizing URLs (Character-level)…")
    tokenizer = CharTokenizer(max_len=200)
    
    X_train_seq = torch.tensor([tokenizer.encode(t) for t in X_train], dtype=torch.long)
    y_train_seq = torch.tensor(y_train, dtype=torch.float)
    X_test_seq = torch.tensor([tokenizer.encode(t) for t in X_test], dtype=torch.long)
    y_test_seq = torch.tensor(y_test, dtype=torch.float)

    train_data = TensorDataset(X_train_seq, y_train_seq)
    train_loader = DataLoader(train_data, batch_size=128, shuffle=True)

    print("\n[4/6] Initialising 1D CNN Model…")
    model = URLCharCNN(
        vocab_size=tokenizer.vocab_size, 
        embed_dim=64, 
        n_filters=100, 
        filter_sizes=[3, 4, 5], 
        output_dim=1, 
        dropout=0.5
    )
    model = model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.BCEWithLogitsLoss()
    criterion = criterion.to(device)

    print(f"\n[5/6] Training CNN for {args.epochs} epochs…")
    for epoch in range(args.epochs):
        t0 = time.time()
        train_loss, train_acc = train_model(model, train_loader, optimizer, criterion, device)
        elapsed = time.time() - t0
        print(f"  Epoch {epoch+1:02} | Time: {elapsed:.1f}s | Train Loss: {train_loss:.4f} | Train Acc: {train_acc*100:.2f}%")

    model.eval()
    with torch.no_grad():
        test_preds = torch.sigmoid(model(X_test_seq.to(device)).squeeze(1)).cpu().numpy()
    
    y_pred = np.round(test_preds).astype(int)
    
    full_report("url_cnn", y_test, y_pred, CLASS_NAMES, "Model: 1D Char CNN (PyTorch)", args.seed)

    print(f"\n[6/6] Saving PyTorch model and tokenizer to {MODELS_DIR}")
    torch.save(model.state_dict(), MODEL_OUT)
    joblib.dump(tokenizer, TOKENIZER_OUT)
    
    print("\n  ✓ 1D CNN Training complete!\n")

if __name__ == "__main__":
    main()
