from pathlib import Path
import joblib
from backend.preprocess import preprocess_text
import numpy as np

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"


def _apply_keyword_heuristics(text: str, category: str, cat_conf: float, priority: str, pri_conf: float) -> tuple:
    text_lower = text.lower()
    category_rules = [
        ("Electricity", ["wire", "wires", "electrical", "electricity", "power line", "utility pole", "sparking", "electric pole", "transformer", "electric shock", "short circuit", "power outage", "street light"]),
        ("Water", ["water leak", "water pipe", "pipe leak", "water supply", "hydrant", "main break", "no water"]),
        ("Drainage", ["drain", "drainage", "sewer", "sewage", "flooding", "clogged drain", "manhole"]),
        ("Waste", ["garbage", "trash", "dumping", "litter", "overflowing bin", "sanitation", "graffiti"]),
        ("Road", ["pothole", "potholes", "asphalt", "traffic light", "traffic signal", "road damage", "street damage"]),
        ("Safety", ["hazard", "fire", "gas leak", "building collapse", "falling tree", "structural damage"]),
    ]
    matched_cat = category
    matched_cat_conf = cat_conf
    for target_cat, keywords in category_rules:
        if any(kw in text_lower for kw in keywords):
            if category == "Other" or cat_conf < 0.85:
                matched_cat = target_cat
                matched_cat_conf = max(cat_conf, 0.90)
                break

    critical_keywords = [
        "live wire", "exposed wire", "sparking", "electric shock", "gas leak",
        "fire", "building collapse", "live electrical", "dangerous", "urgent",
        "hurt", "injured", "risk to life", "life-threatening"
    ]
    matched_pri = priority
    matched_pri_conf = pri_conf
    if any(kw in text_lower for kw in critical_keywords):
        if priority != "Critical":
            matched_pri = "Critical"
            matched_pri_conf = max(pri_conf, 0.95)

    return matched_cat, matched_cat_conf, matched_pri, matched_pri_conf


class Predictor:
    def __init__(self, model_dir: Path = MODEL_DIR):
        self.model_dir = Path(model_dir)
        self._load()

    def _load(self):
        self.cat_model = joblib.load(self.model_dir / "category_model.pkl")
        self.pri_model = joblib.load(self.model_dir / "priority_model.pkl")
        self.vec = joblib.load(self.model_dir / "tfidf_vectorizer.pkl")
        self.cat_le = joblib.load(self.model_dir / "category_label_encoder.pkl")
        self.pri_le = joblib.load(self.model_dir / "priority_label_encoder.pkl")

    def predict(self, text: str) -> dict:
        if not text or not isinstance(text, str) or text.strip() == "":
            return {
                "category": "Other",
                "category_confidence": 0.3,
                "priority": "Medium",
                "priority_confidence": 0.3,
                "note": "empty input fallback",
            }
        cleaned = preprocess_text(text)
        vec = self.vec.transform([cleaned])

        # Category
        try:
            cat_proba = self.cat_model.predict_proba(vec)[0]
            cat_idx = cat_proba.argmax()
            cat_label = self.cat_model.classes_[cat_idx] if hasattr(self.cat_model, "classes_") else self.cat_le.inverse_transform([cat_idx])[0]
            cat_conf = float(cat_proba[cat_idx])
        except Exception:
            pred = self.cat_model.predict(vec)[0]
            cat_label = pred
            cat_conf = 0.6

        # Priority
        try:
            pri_proba = self.pri_model.predict_proba(vec)[0]
            pri_idx = pri_proba.argmax()
            pri_label = self.pri_model.classes_[pri_idx] if hasattr(self.pri_model, "classes_") else self.pri_le.inverse_transform([pri_idx])[0]
            pri_conf = float(pri_proba[pri_idx])
        except Exception:
            pred = self.pri_model.predict(vec)[0]
            pri_label = pred
            pri_conf = 0.6

        cat_label, cat_conf, pri_label, pri_conf = _apply_keyword_heuristics(
            text, str(cat_label), cat_conf, str(pri_label), pri_conf
        )

        return {
            "category": str(cat_label),
            "category_confidence": cat_conf,
            "priority": str(pri_label),
            "priority_confidence": pri_conf,
        }


def predict(text: str) -> dict:
    p = Predictor()
    return p.predict(text)


if __name__ == "__main__":
    # simple interactive test
    p = Predictor()
    examples = [
        "Pothole on Main St causing tire damage",
        "Street light out across 3 blocks",
        "Garbage not collected, bins overflowing",
        "Possible gas leak smell in basement",
    ]
    for e in examples:
        print(e, "->", p.predict(e))
