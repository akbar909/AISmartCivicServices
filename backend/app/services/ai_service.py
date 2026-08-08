"""
AI Classification Service.

Uses pre-trained scikit-learn models (NOT Gemini) for:
- Category classification (7 classes: Road, Water, Waste, Electricity, Drainage, Safety, Other)
- Priority classification (4 levels: Critical, High, Medium, Low)

Models are loaded ONCE at startup via load_models(), not per-request.
The preprocessing pipeline MUST match the one used during training
(see backend/preprocess.py for the original).
"""

import re
import logging
from pathlib import Path
from typing import Optional

import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)

# Path to the .pkl model files
MODEL_DIR = Path(__file__).resolve().parent.parent / "ml_models"

# Global model references — loaded once at startup
_cat_model = None
_pri_model = None
_vectorizer = None
_cat_le = None
_pri_le = None
_models_loaded = False

# ──────────────────────────────────────────────────────────────────
# Preprocessing — EXACT copy from training pipeline (preprocess.py)
# DO NOT modify without also retraining the models.
# ──────────────────────────────────────────────────────────────────

_STOPWORDS = set()
_LEMMATIZER = WordNetLemmatizer()


def ensure_nltk_resources():
    """Download NLTK data if not already present."""
    for resource, name in [
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4"),
        ("corpora/stopwords", "stopwords"),
    ]:
        try:
            nltk.data.find(resource)
        except LookupError:
            nltk.download(name, quiet=True)


def _init_stopwords():
    global _STOPWORDS
    if not _STOPWORDS:
        english = set(stopwords.words("english"))
        # Keep negation words — important for polarity/intent
        negations = {"no", "not", "nor", "n't", "never"}
        _STOPWORDS = english - negations


def clean_text(text: str) -> str:
    """Lightweight cleaning: lowercase, remove urls, special chars, extra spaces."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def lemmatize_tokens(tokens: list) -> list:
    return [_LEMMATIZER.lemmatize(tok) for tok in tokens]


def preprocess_text(text: str) -> str:
    """Full preprocessing pipeline — MUST match training time exactly.

    Steps: lowercase → clean → tokenize → remove stopwords (keep negations) → lemmatize
    """
    if text is None:
        return ""
    _init_stopwords()
    text = clean_text(text)
    if not text:
        return ""
    tokens = text.split()
    tokens = [t for t in tokens if t not in _STOPWORDS]
    tokens = lemmatize_tokens(tokens)
    return " ".join(tokens)


# ──────────────────────────────────────────────────────────────────
# Model loading and prediction
# ──────────────────────────────────────────────────────────────────


def load_models(model_dir: Optional[Path] = None):
    """Load all .pkl models once at startup. Called from FastAPI startup event."""
    global _cat_model, _pri_model, _vectorizer, _cat_le, _pri_le, _models_loaded

    if _models_loaded:
        logger.info("Models already loaded, skipping")
        return

    d = model_dir or MODEL_DIR
    logger.info(f"Loading ML models from {d}")

    try:
        _cat_model = joblib.load(d / "category_model.pkl")
        _pri_model = joblib.load(d / "priority_model.pkl")
        _vectorizer = joblib.load(d / "tfidf_vectorizer.pkl")
        _cat_le = joblib.load(d / "category_label_encoder.pkl")
        _pri_le = joblib.load(d / "priority_label_encoder.pkl")
        _models_loaded = True
        logger.info("All ML models loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load ML models: {e}")
        raise RuntimeError(f"Could not load ML models from {d}: {e}")


def _apply_keyword_heuristics(text: str, category: str, cat_conf: float, priority: str, pri_conf: float) -> tuple:
    """Apply rule-based keyword heuristics for safety hazards and domain-specific terms.
    
    Helps correct ML misclassifications (e.g. electrical wires mapped to 'Other').
    """
    text_lower = text.lower()

    # Rule-based Category Overrides
    category_rules = [
        ("Electricity", ["wire", "wires", "electrical", "electricity", "power line", "utility pole", "sparking", "electric pole", "transformer", "electric shock", "short circuit", "power outage", "street light"]),
        ("Water", ["water leak", "water pipe", "pipe leak", "water supply", "hydrant", "main break", "no water"]),
        ("Drainage", ["drain", "drainage", "sewer", "sewage", "flooding", "clogged drain", "manhole"]),
        ("Waste", ["garbage", "trash", "dumping", "litter", "overflowing bin", "sanitation", "graffiti"]),
        ("Road", ["pothole", "potholes", "asphalt", "traffic light", "traffic signal", "road damage", "street damage"]),
        ("Safety", ["hazard", "fire", "gas leak", "building collapse", "falling tree", "structural damage"]),
    ]

    matched_category = category
    matched_cat_conf = cat_conf

    # Override category if ML predicted 'Other' or low confidence on strong keyword match
    for target_cat, keywords in category_rules:
        if any(kw in text_lower for kw in keywords):
            if category == "Other" or cat_conf < 0.85:
                matched_category = target_cat
                matched_cat_conf = max(cat_conf, 0.90)
                break

    # Rule-based Priority Overrides for Critical Hazards
    critical_keywords = [
        "live wire", "exposed wire", "sparking", "electric shock", "gas leak",
        "fire", "building collapse", "live electrical", "dangerous", "urgent",
        "hurt", "injured", "risk to life", "life-threatening"
    ]

    matched_priority = priority
    matched_pri_conf = pri_conf

    if any(kw in text_lower for kw in critical_keywords):
        if priority != "Critical":
            matched_priority = "Critical"
            matched_pri_conf = max(pri_conf, 0.95)

    return matched_category, matched_cat_conf, matched_priority, matched_pri_conf


def classify_complaint(text: str) -> dict:
    """Classify complaint text using the pre-trained sklearn models + keyword heuristics.

    Returns:
        dict with keys: category, category_confidence, priority, priority_confidence
    """
    if not _models_loaded:
        raise RuntimeError("ML models not loaded. Call load_models() at startup.")

    # Fallback for empty/invalid input
    if not text or not isinstance(text, str) or text.strip() == "":
        return {
            "category": "Other",
            "category_confidence": 0.3,
            "priority": "Medium",
            "priority_confidence": 0.3,
        }

    # Preprocess using the SAME pipeline as training
    cleaned = preprocess_text(text)
    vec = _vectorizer.transform([cleaned])

    # Category prediction with confidence
    try:
        cat_proba = _cat_model.predict_proba(vec)[0]
        cat_idx = cat_proba.argmax()
        cat_label = (
            _cat_model.classes_[cat_idx]
            if hasattr(_cat_model, "classes_")
            else _cat_le.inverse_transform([cat_idx])[0]
        )
        cat_conf = float(cat_proba[cat_idx])
    except Exception:
        pred = _cat_model.predict(vec)[0]
        cat_label = str(pred)
        cat_conf = 0.6

    # Priority prediction with confidence
    try:
        pri_proba = _pri_model.predict_proba(vec)[0]
        pri_idx = pri_proba.argmax()
        pri_label = (
            _pri_model.classes_[pri_idx]
            if hasattr(_pri_model, "classes_")
            else _pri_le.inverse_transform([pri_idx])[0]
        )
        pri_conf = float(pri_proba[pri_idx])
    except Exception:
        pred = _pri_model.predict(vec)[0]
        pri_label = str(pred)
        pri_conf = 0.6

    # Apply keyword heuristics for domain/safety overrides
    cat_label, cat_conf, pri_label, pri_conf = _apply_keyword_heuristics(
        text, str(cat_label), cat_conf, str(pri_label), pri_conf
    )

    return {
        "category": cat_label,
        "category_confidence": round(cat_conf, 4),
        "priority": pri_label,
        "priority_confidence": round(pri_conf, 4),
    }

