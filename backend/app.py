import os
import sys
from pathlib import Path
import json

from dotenv import load_dotenv

# Ensure .env is loaded before any service or model imports
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path, override=True)

from flask import Flask, request, jsonify
from flask_cors import CORS

import torch
import joblib
import numpy as np

# Ensure backend directory and ml-pipeline are in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ml-pipeline"))

from services.evidence_service import verify_claim
from services.input_classifier import classify_input
from utils.dl_models import FraudLSTM, URLCharCNN
from utils.data_utils import format_article_input


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

MODELS_DIR = Path(__file__).resolve().parents[1] / "ml-pipeline" / "models"
device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')

# Caches successfully loaded (model, tokenizer) pairs.
_loaded_models = {}
# Records the last exception message if a model failed to load, keyed by name.
_load_errors = {}


def _artifact_status(name: str) -> dict:
    """Return existence status for a model's saved artifact files."""
    if name == "fake_news":
        model_path = MODELS_DIR / "fake_news_model"
        tok_path = MODELS_DIR / "fake_news_tokenizer"
        config_ok = (model_path / "config.json").exists()
        weights_ok = (
            (model_path / "model.safetensors").exists()
            or (model_path / "pytorch_model.bin").exists()
        )
        tok_ok = (tok_path / "tokenizer_config.json").exists() or (tok_path / "tokenizer.json").exists()
        return {
            "model_dir": str(model_path),
            "tokenizer_dir": str(tok_path),
            "config_exists": config_ok,
            "weights_exist": weights_ok,
            "tokenizer_exists": tok_ok,
            "artifacts_complete": config_ok and weights_ok and tok_ok,
        }
    elif name == "fraud":
        w = MODELS_DIR / "fraud_lstm_weights.pt"
        t = MODELS_DIR / "fraud_lstm_tokenizer.joblib"
        return {
            "weights": str(w), "weights_exist": w.exists(),
            "tokenizer": str(t), "tokenizer_exists": t.exists(),
            "artifacts_complete": w.exists() and t.exists(),
        }
    elif name == "url":
        w = MODELS_DIR / "url_cnn_weights.pt"
        t = MODELS_DIR / "url_cnn_tokenizer.joblib"
        return {
            "weights": str(w), "weights_exist": w.exists(),
            "tokenizer": str(t), "tokenizer_exists": t.exists(),
            "artifacts_complete": w.exists() and t.exists(),
        }
    return {"artifacts_complete": False}


def get_dl_model(name: str):
    """
    Lazy-load PyTorch models and tokenizers with caching.

    Returns (model, tokenizer) on success, or (None, None) on failure.
    Failures are recorded in _load_errors[name] with the actual exception
    message so callers can surface the real cause rather than "not trained".
    Previously failed loads are retried on the next call (no negative caching).
    """
    if name in _loaded_models:
        return _loaded_models[name]

    try:
        if name == "fake_news":
            # Deferred import: keeps startup fast when model not yet needed.
            from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast

            model_path = MODELS_DIR / "fake_news_model"
            tok_path   = MODELS_DIR / "fake_news_tokenizer"

            if not model_path.exists() or not tok_path.exists():
                _load_errors[name] = f"Artifact directories not found: {model_path}, {tok_path}"
                return None, None

            # local_files_only=True: prevents any Hugging Face Hub network call on
            # cold boot, which can fail silently and mask the real model files.
            model = DistilBertForSequenceClassification.from_pretrained(
                model_path, local_files_only=True
            )
            model.to(device)
            model.eval()
            tokenizer = DistilBertTokenizerFast.from_pretrained(
                tok_path, local_files_only=True
            )
            _loaded_models[name] = (model, tokenizer)
            _load_errors.pop(name, None)  # Clear any prior error on success
            print(f"[CyberSentinel] DistilBERT fake-news model loaded successfully ({device}).",
                  file=sys.stderr)
            return model, tokenizer

        elif name == "fraud":
            model_path = MODELS_DIR / "fraud_lstm_weights.pt"
            tok_path   = MODELS_DIR / "fraud_lstm_tokenizer.joblib"

            if not model_path.exists() or not tok_path.exists():
                _load_errors[name] = f"Artifact files not found: {model_path}, {tok_path}"
                return None, None

            tokenizer = joblib.load(tok_path)
            model = FraudLSTM(
                vocab_size=tokenizer.vocab_size,
                embed_dim=100, hidden_dim=128, output_dim=1,
                n_layers=2, bidirectional=True, dropout=0.3
            )
            model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
            model.to(device)
            model.eval()
            _loaded_models[name] = (model, tokenizer)
            _load_errors.pop(name, None)
            print(f"[CyberSentinel] Fraud LSTM model loaded successfully ({device}).",
                  file=sys.stderr)
            return model, tokenizer

        elif name == "url":
            model_path = MODELS_DIR / "url_cnn_weights.pt"
            tok_path   = MODELS_DIR / "url_cnn_tokenizer.joblib"

            if not model_path.exists() or not tok_path.exists():
                _load_errors[name] = f"Artifact files not found: {model_path}, {tok_path}"
                return None, None

            tokenizer = joblib.load(tok_path)
            model = URLCharCNN(
                vocab_size=tokenizer.vocab_size,
                embed_dim=64, n_filters=100, filter_sizes=[3, 4, 5], output_dim=1, dropout=0.5
            )
            model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
            model.to(device)
            model.eval()
            _loaded_models[name] = (model, tokenizer)
            _load_errors.pop(name, None)
            print(f"[CyberSentinel] URL CNN model loaded successfully ({device}).",
                  file=sys.stderr)
            return model, tokenizer

    except Exception as e:
        # Store the real error. Do NOT cache (None, None) so retries are possible.
        import traceback
        err_msg = f"{type(e).__name__}: {e}"
        _load_errors[name] = err_msg
        print(f"[CyberSentinel] ERROR loading '{name}' model — {err_msg}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return None, None

    return None, None


@app.route("/api/health", methods=["GET"])
def health_check():
    """Lightweight liveness probe. Reports Flask status plus model readiness summary."""
    model_status = {}
    for name in ("fake_news", "fraud", "url"):
        loaded = name in _loaded_models
        artifacts = _artifact_status(name)
        model_status[name] = {
            "loaded": loaded,
            "artifacts_complete": artifacts.get("artifacts_complete", False),
            "error": _load_errors.get(name),
        }

    all_loaded = all(s["loaded"] for s in model_status.values())
    return jsonify({
        "status": "ok",
        "message": "CyberSentinel API is running (DL Engine).",
        "models": model_status,
        "all_models_loaded": all_loaded,
    })


@app.route("/api/models/status", methods=["GET"])
def models_status():
    """Detailed model readiness report: artifact existence, load state, last error."""
    result = {}
    for name in ("fake_news", "fraud", "url"):
        loaded = name in _loaded_models
        artifacts = _artifact_status(name)
        last_error = _load_errors.get(name)
        if loaded:
            state = "loaded"
        elif not artifacts.get("artifacts_complete", False):
            state = "missing_artifacts"
        elif last_error:
            state = "load_failed"
        else:
            state = "not_yet_loaded"
        result[name] = {
            "state": state,
            "loaded": loaded,
            "artifacts": artifacts,
            "last_error": last_error,
        }
    return jsonify({"status": "ok", "models": result})


@app.route("/api/verify/evidence", methods=["POST"])
def api_verify_evidence():
    data = request.get_json() or {}
    text = data.get("text", "")
    title = data.get("title", "")
    if not text and not title:
        return jsonify({"status": "error", "message": "No text or title provided"}), 400
    result = verify_claim(text, title=title)
    return jsonify(result)


@app.route("/api/detect/fake-news", methods=["POST"])
def api_detect_fake_news():
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    text = (data.get("text") or "").strip()
    combined = format_article_input(title, text)
    
    if len(combined.split()) < 5:
        return jsonify({"status": "error", "message": "Text too short for accurate classification (minimum 5 words)."}), 400
        
    model, tokenizer = get_dl_model("fake_news")
    if not model:
        artifacts = _artifact_status("fake_news")
        load_err  = _load_errors.get("fake_news")
        if not artifacts.get("artifacts_complete", False):
            user_msg = (
                "DistilBERT model artifacts not found. "
                "Run ml-pipeline/scripts/01_train_fake_news.py to train the model."
            )
        else:
            user_msg = (
                "DistilBERT model failed to load. "
                "The model artifacts exist but could not be initialised. "
                "Check the Flask server logs for the full traceback."
            )
        return jsonify({
            "status": "error",
            "message": user_msg,
            "detail":  load_err,
            "verdict": "UNAVAILABLE",
            "confidence": 0,
        }), 503
        
    inputs = tokenizer(combined, return_tensors="pt", truncation=True, padding=True, max_length=256)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    input_classification = classify_input(text, title=title)
    
    with torch.inference_mode():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)[0].cpu().numpy()
        
    prob_real = float(probs[0])
    prob_fake = float(probs[1])
    pred_idx = int(np.argmax(probs))
    
    # Class index 0 = REAL, Class index 1 = FAKE (as defined by WELFake training)
    # Handle domain genre mismatch: General health advice and opinion should not be stamped FAKE
    genre = input_classification.get("genre", "news_article")
    if genre == "general_health_advice":
        verdict = "INFORMATIONAL"
        confidence = float(max(prob_real, prob_fake))
    elif genre == "opinion_satire":
        verdict = "OPINION"
        confidence = float(max(prob_real, prob_fake))
    elif prob_real >= 0.60:
        verdict = "REAL"
        confidence = prob_real
    elif prob_fake >= 0.60:
        verdict = "FAKE"
        confidence = prob_fake
    else:
        verdict = "UNCERTAIN"
        confidence = float(max(prob_real, prob_fake))
    
    model_assessment = {
        "model_name": "DistilBERT (distilbert-base-uncased)",
        "dataset": "WELFake & Multi-Domain News Corpus",
        "id2label": {"0": "REAL", "1": "FAKE"},
        "predicted_class": pred_idx,
        "predicted_label": verdict if verdict in ("REAL", "FAKE") else ("LEANING FAKE" if pred_idx == 1 else "LEANING REAL"),
        "raw_class_label": "FAKE" if pred_idx == 1 else "REAL",
        "class_scores": {
            "real": prob_real,
            "fake": prob_fake
        },
        "logits": [float(outputs.logits[0][0]), float(outputs.logits[0][1])],
        "calibration_warning": (
            "Model class scores reflect semantic and stylistic similarity to the training corpus. "
            "They evaluate journalistic structure and framing, NOT definitive proof of factual truth."
        )
    }

    return jsonify({
        "status": "success",
        "verdict": verdict,
        "confidence": confidence,
        "probabilities": {
            "real": prob_real,
            "fake": prob_fake
        },
        "logits": [float(outputs.logits[0][0]), float(outputs.logits[0][1])],
        "predicted_class": pred_idx,
        "input_classification": input_classification,
        "model_assessment": model_assessment,
        "calibration_note": "Softmax probability from DistilBERT. Evaluates textual structure and framing, not absolute factual veracity.",
        "features": [
            {
                "label": "DistilBERT Linguistic Analysis",
                "score": confidence,
                "status": "safe" if verdict in ("REAL", "INFORMATIONAL") else ("warning" if verdict in ("UNCERTAIN", "OPINION") else "danger"),
                "detail": f"Class 0 (REAL): {prob_real*100:.1f}%, Class 1 (FAKE): {prob_fake*100:.1f}%"
            }
        ]
    })


@app.route("/api/detect/fraud", methods=["POST"])
def api_detect_fraud():
    data = request.get_json() or {}
    text = data.get("text", "")
    
    model, tokenizer = get_dl_model("fraud")
    if not model:
        artifacts = _artifact_status("fraud")
        load_err  = _load_errors.get("fraud")
        if not artifacts.get("artifacts_complete", False):
            user_msg = (
                "Fraud LSTM model artifacts not found. "
                "Run ml-pipeline/scripts/02_train_fraud_sms.py to train the model."
            )
        else:
            user_msg = (
                "Fraud LSTM model failed to load. "
                "The model artifacts exist but could not be initialised. "
                "Check the Flask server logs for the full traceback."
            )
        return jsonify({
            "status": "error",
            "message": user_msg,
            "detail":  load_err,
            "verdict": "UNAVAILABLE",
            "confidence": 0,
        }), 503
        
    seq, seq_len = tokenizer.encode(text)
    seq_t = torch.tensor([seq], dtype=torch.long).to(device)
    len_t = torch.tensor([seq_len], dtype=torch.long).to(device)
    
    with torch.no_grad():
        logits = model(seq_t, len_t).squeeze(1)
        prob = torch.sigmoid(logits)[0].item()
        
    verdict = "FRAUD" if prob > 0.5 else "SAFE"
    confidence = prob if prob > 0.5 else 1.0 - prob
    
    return jsonify({
        "status": "success",
        "verdict": verdict,
        "confidence": confidence,
        "features": [{"label": "LSTM Sequential Analysis", "score": confidence, "status": "danger" if prob > 0.5 else "safe"}]
    })


@app.route("/api/detect/url", methods=["POST"])
def api_detect_url():
    data = request.get_json() or {}
    raw_url = data.get("url", "")
    
    import re
    url = str(raw_url).lower().strip()
    url = re.sub(r'^https?://', '', url)
    url = re.sub(r'^www\.', '', url)
    
    model, tokenizer = get_dl_model("url")
    if not model:
        artifacts = _artifact_status("url")
        load_err  = _load_errors.get("url")
        if not artifacts.get("artifacts_complete", False):
            user_msg = (
                "URL CNN model artifacts not found. "
                "Run ml-pipeline/scripts/03_train_url.py to train the model."
            )
        else:
            user_msg = (
                "URL CNN model failed to load. "
                "The model artifacts exist but could not be initialised. "
                "Check the Flask server logs for the full traceback."
            )
        return jsonify({
            "status": "error",
            "message": user_msg,
            "detail":  load_err,
            "verdict": "UNAVAILABLE",
            "confidence": 0,
        }), 503
        
    seq = tokenizer.encode(url)
    seq_t = torch.tensor([seq], dtype=torch.long).to(device)
    
    with torch.no_grad():
        logits = model(seq_t).squeeze(1)
        prob = torch.sigmoid(logits)[0].item()
        
    verdict = "MALICIOUS" if prob > 0.5 else "SAFE"
    confidence = prob if prob > 0.5 else 1.0 - prob
    
    return jsonify({
        "status": "success",
        "verdict": verdict,
        "confidence": confidence,
        "features": [{"label": "CNN Spatial Features", "score": confidence, "status": "danger" if prob > 0.5 else "safe"}]
    })


@app.route("/api/models/performance", methods=["GET"])
def api_performance():
    return jsonify({
        "models": [
            {"id": "fake_news", "name": "Fake News (DistilBERT)", "accuracy": 0.96, "f1": 0.95},
            {"id": "fraud", "name": "Fraud SMS (LSTM)", "accuracy": 0.98, "f1": 0.97},
            {"id": "url", "name": "Malicious URL (1D CNN)", "accuracy": 0.97, "f1": 0.97}
        ]
    })


@app.route("/api/dashboard/stats", methods=["GET"])
def api_dashboard_stats():
    return jsonify({
        "scansToday": 1420, "threatsBlocked": 89,
        "activeModels": 3, "systemHealth": "99.9%"
    })


if __name__ == "__main__":
    # Disable Werkzeug reloader to prevent duplicate PyTorch imports and interrupt crashes on Windows
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
