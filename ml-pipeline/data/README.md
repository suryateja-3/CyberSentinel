# Dataset Download Instructions

All raw data files must be placed in `ml-pipeline/data/raw/` before running
the training scripts.  The scripts will **raise a FileNotFoundError** with a
clear message rather than silently substitute synthetic data.

---

## Dataset 1 — WELFake (Fake News Classification)

**Source:** Zenodo  
**Paper:** *WELFake: Word Embedding over Linguistic Features for Fake News Detection*  
**URL:** <https://zenodo.org/record/4561253>  
**License:** Creative Commons Attribution 4.0

### Manual download steps

1. Visit <https://zenodo.org/record/4561253>
2. Download `WELFake_Dataset.csv`
3. Place it at: `ml-pipeline/data/raw/WELFake_Dataset.csv`

### Kaggle API download (alternative)

```bash
pip install kaggle
# Set KAGGLE_USERNAME and KAGGLE_KEY in your environment or ~/.kaggle/kaggle.json
kaggle datasets download saurabhshahane/fake-news-classification -p data/raw --unzip
# Rename if needed:
mv data/raw/WELFake_Dataset.csv data/raw/WELFake_Dataset.csv
```

### Column schema

| Column  | Type   | Description                               |
|---------|--------|-------------------------------------------|
| `title` | string | Article headline                          |
| `text`  | string | Article body                              |
| `label` | int    | `0 = REAL`, `1 = FAKE`                   |

### Label counts (approximate)

| Label     | Count  |
|-----------|--------|
| REAL (0)  | 35,028 |
| FAKE (1)  | 37,106 |

---

## Dataset 2 — UCI SMS Spam Collection (Fraud / Phishing SMS)

**Source:** UCI Machine Learning Repository  
**URL:** <https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection>  
**License:** Public domain

### Automatic download

The script `02_train_fraud_sms.py` will automatically download this file from
the UCI archive if it is not already present. No manual action required.

The file will be saved to: `ml-pipeline/data/raw/SMSSpamCollection`

### Column schema (tab-separated, no header)

| Column | Type   | Description                              |
|--------|--------|------------------------------------------|
| col 0  | string | `ham` = legitimate, `spam` = fraudulent  |
| col 1  | string | SMS message text                         |

### Label counts

| Label       | Count |
|-------------|-------|
| ham (legit) | 4,827 |
| spam        |   747 |

**⚠️ Class Imbalance:** ~87% ham. The training script uses
`class_weight='balanced'` to compensate.

---

## Dataset 3 — Malicious URLs Dataset (URL Classification)

**Source:** Kaggle  
**URL:** <https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset>  
**License:** CC BY 4.0  
**Original source:** PhishTank, OpenPhish, Alexa top-1M, ISCX-URL-2016

### Manual download steps

1. Visit <https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset>
2. Download `malicious_phish.csv`
3. Place it at: `ml-pipeline/data/raw/malicious_phish.csv`

### Kaggle API download

```bash
pip install kaggle
kaggle datasets download sid321axn/malicious-urls-dataset -p data/raw --unzip
```

### Column schema

| Column | Type   | Description                                          |
|--------|--------|------------------------------------------------------|
| `url`  | string | Full URL string                                      |
| `type` | string | `benign`, `phishing`, `defacement`, `malware`        |

The training script **collapses** `phishing`, `defacement`, and `malware` into
a single `malicious` class, giving a binary classification problem.

### Label counts (approximate, after collapsing)

| Label     | Count   |
|-----------|---------|
| benign    | 428,103 |
| malicious | 222,851 |

---

## .gitignore note

The `data/raw/` and `data/processed/` directories are intentionally excluded
from version control to avoid committing large binary datasets and potentially
licensed data.  Add your downloaded files locally and they will not be tracked.
