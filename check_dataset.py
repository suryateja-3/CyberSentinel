import sys
from pathlib import Path
import pandas as pd
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parent / "ml-pipeline"))
from utils.dl_tokenizers import CharTokenizer

def check_dataset():
    data_file = Path(__file__).resolve().parent / "ml-pipeline" / "data" / "raw" / "malicious_phish.csv"
    if not data_file.exists():
        print("Data file not found!")
        return
        
    df = pd.read_csv(data_file, nrows=10)
    print("Dataset head:")
    print(df.head(10))
    
    tokenizer = joblib.load(Path(__file__).resolve().parent / "ml-pipeline" / "models" / "url_cnn_tokenizer.joblib")
    
    print("\nTokenized:")
    for url in df["url"].values[:3]:
        enc = tokenizer.encode(url)
        print(f"URL: {url}")
        print(f"Enc[:20]: {enc[:20]}")

if __name__ == "__main__":
    check_dataset()
