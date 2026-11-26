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
        "https://www.rbi.org.in",
        "https://www.youtube.com/watch?v=Amcm_P7viqk&list=RDnCD2hj6zJEc&index=2",
        "http://secure-login-update-paypal.com",
        "https://google.com",
        "example.com",
        ""
    ]
    
    print("Testing URL Model:")
    for url in urls:
        seq = tokenizer.encode(url)
        seq_t = torch.tensor([seq], dtype=torch.long).to(device)
        with torch.no_grad():
            logits = model(seq_t).squeeze(1)
            prob = torch.sigmoid(logits)[0].item()
        
        verdict = "MALICIOUS" if prob > 0.5 else "SAFE"
        print(f"URL: {url}")
        print(f"Prob: {prob:.4f}, Verdict: {verdict}\n")

if __name__ == "__main__":
    main()
