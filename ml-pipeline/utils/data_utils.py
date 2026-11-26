"""
utils/data_utils.py
===================
Shared helpers for dataset loading, validation, and download.

IMPORTANT
---------
These helpers will RAISE a clear exception rather than silently substitute
synthetic or empty data if a required file is missing or corrupted.
The caller (training script) is expected to abort and print guidance.
"""

from __future__ import annotations

import hashlib
import os
import sys
import urllib.request
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

# Locate the ml-pipeline root regardless of where the script is invoked from.
_HERE = Path(__file__).resolve().parent        # utils/
PIPELINE_ROOT = _HERE.parent                   # ml-pipeline/
DATA_RAW = PIPELINE_ROOT / "data" / "raw"
DATA_PROCESSED = PIPELINE_ROOT / "data" / "processed"
MODELS_DIR = PIPELINE_ROOT / "models"
REPORTS_DIR = PIPELINE_ROOT / "reports"


def ensure_dirs() -> None:
    """Create all required output directories if they do not exist."""
    for d in (DATA_RAW, DATA_PROCESSED, MODELS_DIR, REPORTS_DIR):
        d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Text Preprocessing & Cleaning Helpers
# ---------------------------------------------------------------------------

def clean_wire_datelines(text: str) -> str:
    """
    Remove repetitive wire-service datelines (e.g. 'WASHINGTON (Reuters) -', 'BRUSSELS (Reuters) -')
    so that NLP models learn genuine linguistic, stylistic, and semantic features rather than
    exploiting wire datelines as an artificial classification shortcut.
    """
    import re
    if not text:
        return ""
    # Strip leading wire datelines like 'CITY (Reuters) - ', 'CITY, State (Reuters) - '
    cleaned = re.sub(r'^[A-Z\s,/.\'-]+(?:\([A-Za-z\s,.-]+\)|\[[A-Za-z\s,.-]+\])\s*[-–—]\s*', '', text)
    # Strip standalone 'Reuters - ' or 'Associated Press - ' at the beginning
    cleaned = re.sub(r'^(?:Reuters|Associated Press|AP|AFP|ANI|PTI)\s*[-–—]\s*', '', cleaned, flags=re.IGNORECASE)
    # Strip trailing wire mentions
    cleaned = re.sub(r'\s*[-–—/]\s*(?:Reuters|Associated Press|AP|AFP)\s*$', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def format_article_input(title: str = "", text: str = "") -> str:
    """
    Unify article headline and body combination across training, evaluation, and inference.
    Ensures consistent punctuation and spacing without generating leading periods.
    """
    t = (title or "").strip()
    b = (text or "").strip()
    if t and b:
        sep = " " if t[-1] in ".!?" else ". "
        return f"{t}{sep}{b}"
    return t or b



# ---------------------------------------------------------------------------
# File verification
# ---------------------------------------------------------------------------

def assert_file_exists(path: Path, dataset_name: str, hint: str) -> None:
    """
    Raise FileNotFoundError with a helpful message if *path* does not exist.
    Never silently fall back to synthetic data.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"\n{'='*70}\n"
            f"[ERROR] Required dataset file not found:\n"
            f"  {path}\n\n"
            f"Dataset : {dataset_name}\n"
            f"Action  : {hint}\n"
            f"{'='*70}\n"
            f"See ml-pipeline/data/README.md for full download instructions.\n"
        )


def check_min_rows(df, min_rows: int, dataset_name: str) -> None:
    """
    Raise ValueError if the DataFrame has fewer rows than expected.
    Guards against accidentally loading an empty or truncated file.
    """
    if len(df) < min_rows:
        raise ValueError(
            f"\n[ERROR] Dataset '{dataset_name}' has only {len(df)} rows "
            f"(expected at least {min_rows}).\n"
            f"The file may be truncated or corrupted. "
            f"Please re-download it.\n"
        )


# ---------------------------------------------------------------------------
# Auto-download helpers (for datasets with permissive public URLs)
# ---------------------------------------------------------------------------

def download_file(url: str, dest: Path, description: str = "") -> None:
    """
    Download *url* to *dest* with a simple progress indicator.
    Skips download if the file already exists.
    """
    if dest.exists():
        print(f"  [skip] {dest.name} already present — skipping download.")
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    label = description or dest.name
    print(f"  Downloading {label} …")
    try:
        def _reporthook(count, block_size, total_size):
            if total_size > 0:
                pct = min(count * block_size * 100 // total_size, 100)
                print(f"\r  Progress: {pct}% ", end="", flush=True)

        urllib.request.urlretrieve(url, dest, reporthook=_reporthook)
        print(f"\r  Downloaded {dest.name} ({dest.stat().st_size / 1024:.1f} KB)")
    except Exception as exc:
        # Remove partial file so retries work cleanly
        dest.unlink(missing_ok=True)
        raise RuntimeError(
            f"[ERROR] Failed to download {url}\n"
            f"Reason: {exc}\n"
            f"Please download manually. See data/README.md."
        ) from exc


# ---------------------------------------------------------------------------
# Reproducibility helper
# ---------------------------------------------------------------------------

def report_split_info(y_train, y_test, label_names: dict) -> None:
    """Print class distribution in train and test sets for transparency."""
    import pandas as pd

    print("\n  -- Class distribution ------------------------------")
    for split_name, y in [("Train", y_train), ("Test", y_test)]:
        counts = pd.Series(y).value_counts().sort_index()
        total = len(y)
        rows = []
        for cls_idx, cnt in counts.items():
            name = label_names.get(cls_idx, str(cls_idx))
            rows.append(f"    {split_name:5s}  [{cls_idx}] {name:20s}  "
                        f"{cnt:6d}  ({cnt/total*100:.1f}%)")
        print("\n".join(rows))
    print()
