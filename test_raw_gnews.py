import sys
from pathlib import Path
from dotenv import load_dotenv
import os
import requests

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

def main():
    api_key = os.environ.get("GNEWS_API_KEY")
    print(f"API Key present: {'Yes' if api_key else 'No'}")
    
    params = {
        "q": "NASA",
        "lang": "en",
        "apikey": api_key,
        "max": 5
    }
    
    response = requests.get("https://gnews.io/api/v4/search", params=params)
    print(response.status_code)
    print(response.text)

if __name__ == "__main__":
    main()
