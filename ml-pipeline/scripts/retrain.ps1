# =============================================================================
# retrain.ps1 — CyberSentinel ML Pipeline Retraining (Windows PowerShell)
# =============================================================================
#
# Usage:
#   cd ml-pipeline
#   powershell -ExecutionPolicy Bypass -File scripts\retrain.ps1
#
# Prerequisites:
#   1. Python 3.10+ with requirements installed
#      pip install -r requirements.txt
#   2. Datasets downloaded to data\raw\
#      See data\README.md for download instructions
#
# What this script does:
#   1. Trains the Fake News classifier (01_train_fake_news.py)
#   2. Trains the Fraud / SMS classifier (02_train_fraud_sms.py)
#   3. Trains the URL classifier (03_train_url.py)
#   4. Runs evaluation / sanity check on saved models (04_evaluate_all.py)
#
# Each step aborts the pipeline on failure ($LASTEXITCODE != 0).
# =============================================================================

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir   = Split-Path -Parent $ScriptDir

$Seed     = if ($env:SEED)      { $env:SEED }      else { "42" }
$TestSize = if ($env:TEST_SIZE) { $env:TEST_SIZE }  else { "0.2" }

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " CyberSentinel — Full ML Training Pipeline (Windows)"        -ForegroundColor Cyan
Write-Host " Root    : $RootDir"
Write-Host " Seed    : $Seed"
Write-Host " Test%   : $TestSize"
Write-Host "============================================================" -ForegroundColor Cyan

Set-Location $RootDir

Write-Host "`n[Step 1/4] Training Fake News Classifier..." -ForegroundColor Yellow
python scripts\01_train_fake_news.py --seed $Seed --test-size $TestSize
if ($LASTEXITCODE -ne 0) {
    Write-Error "[ABORT] Fake News training failed (exit code $LASTEXITCODE)."
    exit 1
}

Write-Host "`n[Step 2/4] Training Fraud / SMS Phishing Classifier..." -ForegroundColor Yellow
python scripts\02_train_fraud_sms.py --seed $Seed --test-size $TestSize
if ($LASTEXITCODE -ne 0) {
    Write-Error "[ABORT] Fraud SMS training failed (exit code $LASTEXITCODE)."
    exit 1
}

Write-Host "`n[Step 3/4] Training URL / Phishing Classifier..." -ForegroundColor Yellow
python scripts\03_train_url.py --seed $Seed --test-size $TestSize
if ($LASTEXITCODE -ne 0) {
    Write-Error "[ABORT] URL training failed (exit code $LASTEXITCODE)."
    exit 1
}

Write-Host "`n[Step 4/4] Running sanity checks on saved models..." -ForegroundColor Yellow
python scripts\04_evaluate_all.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "[ABORT] Evaluation script failed (exit code $LASTEXITCODE)."
    exit 1
}

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host " All models trained and saved to : $RootDir\models\"          -ForegroundColor Green
Write-Host " Metrics saved to                : $RootDir\reports\"         -ForegroundColor Green
Write-Host "============================================================"  -ForegroundColor Green
