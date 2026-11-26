#!/usr/bin/env bash
# =============================================================================
# retrain.sh — CyberSentinel ML Pipeline Retraining Script (Linux / macOS)
# =============================================================================
#
# Usage:
#   bash scripts/retrain.sh [--seed 42] [--test-size 0.2]
#
# Run from the ml-pipeline/ directory:
#   cd ml-pipeline
#   bash scripts/retrain.sh
#
# Prerequisites:
#   1. Python 3.10+ with all requirements installed
#      pip install -r requirements.txt
#   2. Datasets downloaded to data/raw/
#      See data/README.md for download instructions
#
# What this script does:
#   1. Trains the Fake News classifier (01_train_fake_news.py)
#   2. Trains the Fraud / SMS classifier (02_train_fraud_sms.py)
#   3. Trains the URL classifier (03_train_url.py)
#   4. Runs evaluation / sanity check on all saved models (04_evaluate_all.py)
#
# Each script exits with code 1 on error — the pipeline aborts immediately.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Default hyperparameters (override via env vars or args)
SEED="${SEED:-42}"
TEST_SIZE="${TEST_SIZE:-0.2}"

echo "============================================================"
echo " CyberSentinel — Full ML Training Pipeline"
echo " Root  : $ROOT_DIR"
echo " Seed  : $SEED"
echo " Test% : $TEST_SIZE"
echo "============================================================"

cd "$ROOT_DIR"

echo ""
echo "[Step 1/4] Training Fake News Classifier..."
python scripts/01_train_fake_news.py --seed "$SEED" --test-size "$TEST_SIZE"

echo ""
echo "[Step 2/4] Training Fraud / SMS Phishing Classifier..."
python scripts/02_train_fraud_sms.py --seed "$SEED" --test-size "$TEST_SIZE"

echo ""
echo "[Step 3/4] Training URL / Phishing Classifier..."
python scripts/03_train_url.py --seed "$SEED" --test-size "$TEST_SIZE"

echo ""
echo "[Step 4/4] Running sanity checks on saved models..."
python scripts/04_evaluate_all.py

echo ""
echo "============================================================"
echo " ✓  All models trained and saved to: $ROOT_DIR/models/"
echo " ✓  Metrics saved to               : $ROOT_DIR/reports/"
echo "============================================================"
