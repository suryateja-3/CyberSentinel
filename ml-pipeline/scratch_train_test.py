"""
ml-pipeline/scratch_train_test.py
Test script for enhanced DistilBERT training with wire de-biasing,
domain diversity data, validation loop, early stopping, and regression test.
"""

import sys
import time
import os
from pathlib import Path

pipeline_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(pipeline_dir))

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast, get_linear_schedule_with_warmup
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score

from utils.data_utils import clean_wire_datelines, format_article_input, DATA_RAW

def load_enhanced_dataset(sample_size=2400, seed=42):
    print("[1/5] Loading and de-biasing WELFake dataset...")
    wf_file = DATA_RAW / "WELFake_Dataset.csv"
    div_file = DATA_RAW / "domain_diversity_news.csv"

    df_wf = pd.read_csv(
        wf_file,
        usecols=lambda c: c.strip().lower() in ["title", "text", "label"],
        low_memory=False
    )
    df_wf.columns = df_wf.columns.str.strip().str.lower()
    df_wf = df_wf.dropna(subset=["label"])
    df_wf["label"] = df_wf["label"].astype(int)
    df_wf["title"] = df_wf["title"].fillna("")
    df_wf["text"] = df_wf["text"].fillna("")

    # Clean wire datelines to remove shortcut
    df_wf["cleaned_text"] = df_wf["text"].apply(clean_wire_datelines)
    
    # Format inputs consistently
    df_wf["combined"] = [
        format_article_input(t, txt) for t, txt in zip(df_wf["title"], df_wf["cleaned_text"])
    ]

    # Drop short articles and duplicates
    df_wf = df_wf[df_wf["combined"].str.split().str.len() >= 10]
    df_wf = df_wf.drop_duplicates(subset=["combined"]).reset_index(drop=True)

    # Balanced sample from WELFake
    n_per_class = sample_size // 2
    df_0 = df_wf[df_wf["label"] == 0].sample(n=min(n_per_class, len(df_wf[df_wf["label"] == 0])), random_state=seed)
    df_1 = df_wf[df_wf["label"] == 1].sample(n=min(n_per_class, len(df_wf[df_wf["label"] == 1])), random_state=seed)
    df_sampled = pd.concat([df_0, df_1], ignore_index=True)

    # Load domain diversity data
    if div_file.exists():
        df_div = pd.read_csv(div_file)
        df_div["title"] = df_div["title"].fillna("")
        df_div["text"] = df_div["text"].fillna("")
        df_div["combined"] = [
            format_article_input(t, txt) for t, txt in zip(df_div["title"], df_div["text"])
        ]
        df_div = df_div[["combined", "label"]].dropna()
        print(f"  Adding {len(df_div)} curated multi-domain articles (Tech, Business, Science, Health, Figures).")
        # Oversample diversity data slightly (weight=3) so domain balance is impactful in the sample
        div_augmented = pd.concat([df_div] * 3, ignore_index=True)
        df_all = pd.concat([df_sampled[["combined", "label"]], div_augmented], ignore_index=True)
    else:
        df_all = df_sampled[["combined", "label"]]

    df_all = df_all.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    print(f"  Total dataset size: {len(df_all)} articles (Class 0: {(df_all['label']==0).sum()}, Class 1: {(df_all['label']==1).sum()})")
    return df_all["combined"].tolist(), df_all["label"].tolist()

def main():
    seed = 42
    torch.manual_seed(seed)
    np.random.seed(seed)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    X, y = load_enhanced_dataset(sample_size=2000, seed=seed)

    # 70% Train, 15% Val, 15% Test
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.15, stratify=y, random_state=seed
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.1765, stratify=y_train_val, random_state=seed
    )

    print(f"Split sizes: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")

    tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')

    def make_dataset(texts, labels):
        enc = tokenizer(texts, truncation=True, padding=True, max_length=160, return_tensors='pt')
        return TensorDataset(enc['input_ids'], enc['attention_mask'], torch.tensor(labels, dtype=torch.long))

    train_loader = DataLoader(make_dataset(X_train, y_train), batch_size=16, shuffle=True)
    val_loader = DataLoader(make_dataset(X_val, y_val), batch_size=32)
    test_loader = DataLoader(make_dataset(X_test, y_test), batch_size=32)

    id2label = {0: "REAL", 1: "FAKE"}
    label2id = {"REAL": 0, "FAKE": 1}

    model = DistilBertForSequenceClassification.from_pretrained(
        'distilbert-base-uncased',
        num_labels=2,
        id2label=id2label,
        label2id=label2id
    )

    # Freeze lower layers (0, 1, 2) to preserve general encyclopedic / linguistic knowledge
    for param in model.distilbert.embeddings.parameters():
        param.requires_grad = False
    for layer in model.distilbert.transformer.layer[:3]:
        for param in layer.parameters():
            param.requires_grad = False

    model.to(device)

    # Differential learning rates: 2e-5 for remaining transformer layers, 1e-4 for classifier head
    classifier_params = list(model.pre_classifier.parameters()) + list(model.classifier.parameters())
    transformer_params = [p for p in model.distilbert.transformer.layer[3:].parameters() if p.requires_grad]

    optimizer = torch.optim.AdamW([
        {'params': transformer_params, 'lr': 2e-5, 'weight_decay': 0.01},
        {'params': classifier_params, 'lr': 1e-4, 'weight_decay': 0.01}
    ])

    epochs = 2
    total_steps = len(train_loader) * epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=int(total_steps * 0.1), num_training_steps=total_steps)

    print(f"\n[3/5] Fine-tuning DistilBERT for {epochs} epochs...")
    best_val_f1 = 0.0
    best_state_dict = None

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        t0 = time.time()
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids, attention_mask, labels = [b.to(device) for b in batch]
            out = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = out.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()
            train_loss += loss.item()

        elapsed = time.time() - t0
        avg_train_loss = train_loss / len(train_loader)

        # Validation
        model.eval()
        val_preds, val_targets = [], []
        val_loss = 0.0
        with torch.no_grad():
            for batch in val_loader:
                input_ids, attention_mask, labels = [b.to(device) for b in batch]
                out = model(input_ids, attention_mask=attention_mask, labels=labels)
                val_loss += out.loss.item()
                preds = torch.argmax(out.logits, dim=-1)
                val_preds.extend(preds.cpu().numpy())
                val_targets.extend(labels.cpu().numpy())

        avg_val_loss = val_loss / len(val_loader)
        val_acc = accuracy_score(val_targets, val_preds)
        val_f1 = f1_score(val_targets, val_preds, average='macro')
        print(f"  Epoch {epoch+1:02} | Time: {elapsed:.1f}s | Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} | Val Acc: {val_acc*100:.2f}% | Val F1: {val_f1*100:.2f}%")

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_state_dict = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    if best_state_dict:
        model.load_state_dict(best_state_dict)

    print("\n[4/5] Evaluating on Untouched Held-Out Test Set...")
    model.eval()
    test_preds, test_probs = [], []
    with torch.no_grad():
        for batch in test_loader:
            input_ids, attention_mask, _ = [b.to(device) for b in batch]
            out = model(input_ids, attention_mask=attention_mask)
            probs = torch.softmax(out.logits, dim=-1).cpu().numpy()
            preds = np.argmax(probs, axis=-1)
            test_probs.extend(probs.tolist())
            test_preds.extend(preds.tolist())

    print("\nTest Classification Report:")
    print(classification_report(y_test, test_preds, target_names=["REAL (0)", "FAKE (1)"], digits=4))

    print("\n[5/5] Regression Test: Mark Zuckerberg Factual Statement...")
    zuck_text = "Mark Zuckerberg is famous for co-founding Facebook (now Meta Platforms) and serving as its long-time chief executive officer."
    enc = tokenizer(zuck_text, return_tensors='pt', truncation=True, padding=True, max_length=160)
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.no_grad():
        out = model(**enc)
        probs = torch.softmax(out.logits, dim=-1)[0].cpu().numpy()
        pred = int(np.argmax(probs))

    prob_real = float(probs[0])
    prob_fake = float(probs[1])
    verdict = id2label[pred]
    print(f"Input: \"{zuck_text}\"")
    print(f"Logits: {out.logits[0].tolist()}")
    print(f"Class 0 (REAL): {prob_real*100:.2f}% | Class 1 (FAKE): {prob_fake*100:.2f}%")
    print(f"Predicted Class: {pred} ({verdict})")

if __name__ == "__main__":
    main()
