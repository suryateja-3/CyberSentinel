import sys
from pathlib import Path
import torch
import joblib
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / "ml-pipeline"))
from utils.dl_models import URLCharCNN

def main():
    data_file = Path(__file__).resolve().parent / "ml-pipeline" / "data" / "raw" / "malicious_phish.csv"
    df = pd.read_csv(data_file)
    df["label"] = (df["type"] != "benign").astype(int)
    # Take a small random sample
    df = df.sample(100, random_state=42)
    urls = df["url"].values
    labels = df["label"].values

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
    
    print("Predictions on sample:")
    for url, label in zip(urls[:20], labels[:20]):
        seq = tokenizer.encode(url)
        seq_t = torch.tensor([seq], dtype=torch.long).to(device)
        with torch.no_grad():
            prob = torch.sigmoid(model(seq_t).squeeze(1))[0].item()
        
        pred = 1 if prob > 0.5 else 0
        print(f"[{'CORRECT' if pred == label else 'WRONG'}] True: {label}, Pred: {pred} ({prob:.4f}) | {url}")

if __name__ == "__main__":
    main()
