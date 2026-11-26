import sys
from pathlib import Path
import torch
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix

sys.path.insert(0, str(Path(__file__).resolve().parent / "ml-pipeline"))
from utils.dl_models import URLCharCNN

def load_data():
    data_file = Path(__file__).resolve().parent / "ml-pipeline" / "data" / "raw" / "malicious_phish.csv"
    df = pd.read_csv(data_file)
    df["label"] = (df["type"] != "benign").astype(int)
    # Take a small random sample to evaluate
    df = df.sample(5000, random_state=42)
    return df["url"].values, df["label"].values

def main():
    models_dir = Path(__file__).resolve().parent / "ml-pipeline" / "models"
    model_path = models_dir / "url_cnn_weights.pt"
    tok_path = models_dir / "url_cnn_tokenizer.joblib"
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    tokenizer = joblib.load(tok_path)
    model = URLCharCNN(
        vocab_size=tokenizer.vocab_size,
        embed_dim=64, n_filters=100, filter_sizes=[3, 4, 5], output_dim=1, dropout=0.5
    )
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    
    X, y_true = load_data()
    
    print("Evaluating...")
    
    # Process in batches to avoid OOM
    batch_size = 128
    y_pred = []
    
    for i in range(0, len(X), batch_size):
        batch_urls = X[i:i+batch_size]
        seqs = [tokenizer.encode(url) for url in batch_urls]
        seq_t = torch.tensor(seqs, dtype=torch.long).to(device)
        
        with torch.no_grad():
            logits = model(seq_t).squeeze(1)
            # if batch size is 1, squeeze(1) might do nothing if dimension is not 1!
            # wait, model returns [batch, 1]. squeeze(1) makes it [batch]. If batch is 1, it's [1].
            probs = torch.sigmoid(logits).cpu().numpy()
            
        preds = (probs > 0.5).astype(int)
        
        # handle scalar return if batch size is 1
        if preds.ndim == 0:
            y_pred.append(int(preds))
        else:
            y_pred.extend(preds.tolist())
            
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=["BENIGN", "MALICIOUS"]))

if __name__ == "__main__":
    main()
