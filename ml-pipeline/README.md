# CyberSentinel — ML Training Pipeline

A fully reproducible, documented machine-learning pipeline that trains three
threat-detection classifiers and saves each trained model with its complete
preprocessing pipeline for use by the Flask backend.

---

## 1. Models & Datasets

### 1.1 Fake News Classifier
| Item | Detail |
|------|--------|
| **Algorithm** | TF-IDF (unigrams + bigrams) → Logistic Regression |
| **Dataset** | [WELFake](https://zenodo.org/record/4561253) — 72,134 labelled news articles (Kaggle mirror: `saurabhshahane/fake-news-classification`) |
| **Labels** | `0 = REAL`, `1 = FAKE` |
| **Baseline accuracy** | ~93–96 % (depends on split seed) |
| **Key limitation** | Trained on English political news; may not generalise to satire or non-English text |
| **Class balance** | Approximately 50/50 — no special resampling needed |

### 1.2 Online Fraud / SMS Phishing Classifier
| Item | Detail |
|------|--------|
| **Algorithm** | TF-IDF (char + word n-grams) → Logistic Regression |
| **Dataset** | [UCI SMS Spam Collection](https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection) — 5,574 SMS messages |
| **Labels** | `ham = LEGITIMATE`, `spam = PHISHING / FRAUD` |
| **Baseline accuracy** | ~97–99 % |
| **Key limitation** | Small dataset; heavy class imbalance (~87 % ham). Uses `class_weight='balanced'` |
| **Class balance** | ≈ 87 % ham / 13 % spam → class weights applied |

### 1.3 Malicious URL Classifier
| Item | Detail |
|------|--------|
| **Algorithm** | Lexical URL feature extractor → Random Forest |
| **Dataset** | [Malicious URLs Dataset (Kaggle)](https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset) — ~651 K URLs, 4 classes collapsed to binary |
| **Labels** | `benign = 0`, `malicious = 1` (phishing + defacement + malware) |
| **Baseline accuracy** | ~96–98 % |
| **Key limitation** | Lexical features only — no live DNS/SSL checks. Adversarial URLs that mimic benign lexical patterns may evade detection |
| **Class balance** | ≈ 57 % benign / 43 % malicious — acceptable balance |

---

## 2. Repository Layout

```
ml-pipeline/
├── README.md                   ← This file
├── requirements.txt            ← Pinned Python dependencies
├── data/
│   ├── README.md               ← Dataset download instructions
│   ├── raw/                    ← Downloaded raw files (git-ignored)
│   └── processed/              ← Cleaned CSV files (git-ignored)
├── models/                     ← Saved .joblib pipelines (git-ignored)
├── reports/                    ← Auto-generated metric text files
├── utils/
│   ├── __init__.py
│   ├── data_utils.py           ← Shared download / validation helpers
│   ├── metrics_utils.py        ← Reporting & confusion matrix helpers
│   └── url_features.py         ← URL lexical feature extractor
└── scripts/
    ├── 01_train_fake_news.py   ← Train & save fake news classifier
    ├── 02_train_fraud_sms.py   ← Train & save fraud/SMS classifier
    ├── 03_train_url.py         ← Train & save URL classifier
    ├── 04_evaluate_all.py      ← Load saved models & run inference examples
    ├── retrain.sh              ← Linux/macOS: run all three scripts in order
    └── retrain.ps1             ← Windows PowerShell: run all three scripts
```

---

## 3. Setup

### Prerequisites
- Python 3.10 or later
- pip

### Install dependencies

```bash
cd ml-pipeline
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

---

## 4. Download Datasets

See [`data/README.md`](data/README.md) for step-by-step dataset download
instructions.  The scripts will **abort with a clear error** rather than
silently use synthetic data if the dataset files are missing.

---

## 5. Train All Models

```bash
# Linux / macOS
bash scripts/retrain.sh

# Windows PowerShell
powershell scripts/retrain.ps1
```

Or run each script individually:

```bash
python scripts/01_train_fake_news.py
python scripts/02_train_fraud_sms.py
python scripts/03_train_url.py
```

Each script prints a full classification report and saves:
- `models/<name>_pipeline.joblib` — the serialised sklearn Pipeline
- `reports/<name>_metrics.txt` — the text classification report

---

## 6. Evaluate / Sanity-Check Saved Models

```bash
python scripts/04_evaluate_all.py
```

This loads each saved `.joblib` pipeline and runs a handful of clearly labelled
**demonstration examples** to verify the models are correctly loaded and
returning sensible predictions.

---

## 7. Connect to Flask API

Each `.joblib` file contains a complete `sklearn.pipeline.Pipeline` that you can
load in Flask like this:

```python
import joblib

fake_news_pipeline = joblib.load("models/fake_news_pipeline.joblib")

# Returns "FAKE" or "REAL"
label = fake_news_pipeline.predict(["Breaking: Scientists discover water on Mars"])[0]
```

See the `04_evaluate_all.py` script for usage examples for all three models.

---

## 8. Class Imbalance Handling

| Model | Strategy |
|-------|----------|
| Fake News | None needed — dataset is balanced |
| SMS Fraud | `class_weight='balanced'` in Logistic Regression |
| URL | `class_weight='balanced'` in Random Forest |

---

## 9. Limitations & Ethical Considerations

- These models are trained on **historical, English-language** datasets.
  They should not be used as the sole decision-making system for real-world
  threat classification without human review.
- SMS Spam: The 5,574-sample UCI dataset is small by modern standards.
  Performance on production data may be lower.
- URL features are **lexical only** (no DNS, WHOIS, or live content fetching).
  Sophisticated adversaries can evade lexical classifiers.
- Fake news detection is inherently subjective in borderline cases.

---

## 10. Reproducibility

All scripts accept a `--seed` argument (default `42`) to fix the random state
for train/test split and model training, ensuring identical results across runs
on the same dataset.
