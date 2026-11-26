import sys
from pathlib import Path
import torch

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))
from app import get_dl_model

def main():
    model, tokenizer = get_dl_model("url")
    if not model:
        print("Model not loaded.")
        return
        
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    urls = [
        "rbi.org.in",
        "https://www.rbi.org.in",
        "youtube.com/watch?v=Amcm_P7viqk&list=RDnCD2hj6zJEc&index=2",
        "https://www.youtube.com/watch?v=Amcm_P7viqk&list=RDnCD2hj6zJEc&index=2",
        "google.com",
        "https://google.com",
        "google.com/search?q=hello",
        "http://www.google.com"
    ]
    
    for url in urls:
        seq = tokenizer.encode(url)
        seq_t = torch.tensor([seq], dtype=torch.long).to(device)
        with torch.no_grad():
            prob = torch.sigmoid(model(seq_t).squeeze(1))[0].item()
        
        print(f"URL: {url} -> {prob:.4f}")

if __name__ == "__main__":
    main()
