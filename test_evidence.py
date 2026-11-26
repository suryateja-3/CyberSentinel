import sys
from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))
from services.evidence_service import verify_claim

def main():
    print(f"API Key present: {'Yes' if os.environ.get('GNEWS_API_KEY') else 'No'}")
    result = verify_claim("NASA launched a new rover")
    print(result)

if __name__ == "__main__":
    main()
