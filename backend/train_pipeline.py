"""
End-to-end training pipeline for civic complaint category and priority models.

Run: python src/train_pipeline.py
"""
from pathlib import Path
import pandas as pd
import numpy as np
import random
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.utils import resample

from backend.preprocess import preprocess_text
from backend.features import build_tfidf

logging.basicConfig(level=logging.INFO)


DATA_PATH = Path(__file__).resolve().parents[1] / "311-service-requests.csv"
OUT_DIR = Path(__file__).resolve().parents[1] / "models"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR = Path(__file__).resolve().parents[1] / "outputs"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


CATEGORY_MAP = {
    # Road-related
    "pothole": "Road",
    "street condition": "Road",
    "traffic signal condition": "Road",
    "blocked driveway": "Other",
    "illegal parking": "Other",
    # Water
    "water system": "Water",
    "hydrant leaking": "Water",
    # Waste / sanitation
    "sanitation condition": "Waste",
    "garbage": "Waste",
    "graffiti": "Waste",
    # Electricity
    "street light condition": "Electricity",
    "street light out": "Electricity",
    # Drainage / sewer
    "sewer": "Drainage",
    "sewer backup": "Drainage",
    # Safety
    "noise": "Safety",
    "panhandling": "Safety",
    "homeless encampment": "Safety",
    # Rodent/Health map to Other
    "rodent": "Other",
}


def map_category(raw: str) -> str:
    if not isinstance(raw, str):
        return "Other"
    r = raw.lower()
    for k, v in CATEGORY_MAP.items():
        if k in r:
            return v
    # fallback heuristics
    if "noise" in r or "panhandling" in r:
        return "Safety"
    return "Other"


CRITICAL_KEYWORDS = [
    "exposed wire",
    "gas leak",
    "fire hazard",
    "collapse",
    "major flooding",
    "live wire",
    "structural damage",
]

HIGH_KEYWORDS = [
    "large water leak",
    "sewage",
    "sewage backup",
    "major road",
    "blocked bridge",
    "no power",
    "outage",
]

MEDIUM_KEYWORDS = [
    "pothole",
    "minor leak",
    "overflow",
    "broken",
    "damaged",
]

LOW_KEYWORDS = [
    "graffiti",
    "litter",
    "minor debris",
    "flicker",
]


def derive_priority(text: str, category: str) -> str:
    """Rule-based priority labeling.

    Logic (explainable):
    - If any critical keyword is present -> Critical
    - Else if any high keyword present -> High
    - Else if any medium keyword present -> Medium
    - Else if any low keyword present -> Low
    - Else use category-based defaults (Safety/Electricity/Water -> High, Road/Drainage -> Medium, Waste/Other -> Low)

    This is intentionally transparent and editable.
    """
    t = (text or "").lower()
    for kw in CRITICAL_KEYWORDS:
        if kw in t:
            return "Critical"
    for kw in HIGH_KEYWORDS:
        if kw in t:
            return "High"
    for kw in MEDIUM_KEYWORDS:
        if kw in t:
            return "Medium"
    for kw in LOW_KEYWORDS:
        if kw in t:
            return "Low"

    defaults = {
        "Safety": "High",
        "Electricity": "High",
        "Water": "High",
        "Road": "Medium",
        "Drainage": "Medium",
        "Waste": "Low",
        "Other": "Low",
    }
    return defaults.get(category, "Medium")


def load_and_prepare(n_rows: int = None):
    usecols = [
        "Created Date",
        "Agency",
        "Complaint Type",
        "Descriptor",
        "City",
        "Borough",
        "Status",
    ]
    # Use chunks to handle large files gracefully
    chunks = pd.read_csv(DATA_PATH, usecols=lambda c: c in usecols, parse_dates=["Created Date"], chunksize=100000)
    df = pd.concat(chunks, ignore_index=True)
    logging.info("Loaded %d rows", len(df))

    # Keep relevant columns
    df = df[[c for c in usecols if c in df.columns]]

    # Create text field from Complaint Type + Descriptor
    df["text_raw"] = df["Complaint Type"].fillna("") + " " + df.get("Descriptor", "").fillna("")
    df = df[df["text_raw"].str.strip() != ""]

    # Deduplicate exact (near-identical detection could be added later)
    df["text_norm"] = df["text_raw"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
    df = df.drop_duplicates(subset=["text_norm"]).copy()

    # Map categories
    df["category"] = df["Complaint Type"].apply(map_category)

    # If n_rows specified, sample a subset balanced across categories
    if n_rows is None:
        n_rows = min(12000, max(8000, len(df)))
    aim_per_class = max(300, n_rows // 7)

    frames = []
    for cat, group in df.groupby("category"):
        if len(group) < 300:
            # oversample minority classes to reach 300 (defensible)
            grp = resample(group, replace=True, n_samples=300, random_state=42)
        else:
            grp = group.sample(n=min(len(group), aim_per_class), random_state=42)
        frames.append(grp)
    df_bal = pd.concat(frames).sample(frac=1, random_state=42).reset_index(drop=True)
    logging.info("Balanced dataset to %d rows; class counts:\n%s", len(df_bal), df_bal["category"].value_counts())

    # Preprocess text column (save both raw and preprocessed)
    df_bal["text"] = df_bal["text_raw"].apply(preprocess_text)

    # Derive priority labels
    df_bal["priority"] = df_bal.apply(lambda r: derive_priority(r["text_raw"], r["category"]), axis=1)

    return df_bal


def evaluate_and_report(y_true, y_pred, labels, out_prefix: Path):
    report = classification_report(y_true, y_pred, labels=labels, output_dict=True)
    print(classification_report(y_true, y_pred, labels=labels))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    # plot
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=labels, yticklabels=labels, cmap="Blues")
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    plt.title(f"Confusion matrix: {out_prefix.name}")
    out_file = out_prefix.parent / f"{out_prefix.name}_confusion.png"
    plt.savefig(out_file)
    plt.close()
    return report, out_file


def train_models(X_train, X_test, y_train, y_test, task_name: str):
    results = {}
    label_encoder = LabelEncoder()
    y_train_enc = label_encoder.fit_transform(y_train)
    y_test_enc = label_encoder.transform(y_test)

    models = {
        "LogisticRegression": LogisticRegression(max_iter=2000),
        "SVC": SVC(kernel="linear", probability=True),
        "RandomForest": RandomForestClassifier(n_jobs=-1),
    }

    param_grid = {
        "LogisticRegression": {"C": [0.01, 0.1, 1, 10]},
        "SVC": {"C": [0.1, 1, 10]},
        "RandomForest": {"n_estimators": [100, 300], "max_depth": [None, 20, 50]},
    }

    best_model = None
    best_score = -1

    for name, model in models.items():
        print(f"Training {name} for {task_name}...")
        gs = GridSearchCV(model, param_grid[name], scoring="f1_weighted", cv=5, n_jobs=-1)
        gs.fit(X_train, y_train)
        pred = gs.predict(X_test)
        score = f1_score(y_test, pred, average="weighted")
        results[name] = {"model": gs.best_estimator_, "f1_weighted": score, "cv_best_params": gs.best_params_}
        print(f"{name} f1_weighted={score:.4f}")
        if score > best_score:
            best_score = score
            best_model = gs.best_estimator_

    return best_model, results, label_encoder


def top_misclassified_examples(df_test, y_true, y_pred, n=10):
    df_test = df_test.copy()
    df_test["true"] = y_true
    df_test["pred"] = y_pred
    mis = df_test[df_test["true"] != df_test["pred"]]
    return mis[["text_raw", "text", "true", "pred"]].head(n)


def main():
    df = load_and_prepare(n_rows=10000)
    # Vectorize
    vec, X = build_tfidf(df["text"].fillna(""), max_features=8000)

    # Category model
    X_cat = X
    y_cat = df["category"]
    Xc_train, Xc_test, yc_train, yc_test, idx_train, idx_test = train_test_split(
        X_cat, y_cat, df.index, test_size=0.2, stratify=y_cat, random_state=42
    )

    best_cat_model, cat_results, cat_le = train_models(Xc_train, Xc_test, yc_train, yc_test, "category")
    # Evaluate category
    y_cat_pred = best_cat_model.predict(Xc_test)
    cat_report, cat_cm_file = evaluate_and_report(yc_test, y_cat_pred, labels=sorted(df["category"].unique()), out_prefix=OUT_DIR / "category")

    # Priority model (same features)
    X_pri = X
    y_pri = df["priority"]
    if y_pri.value_counts().min() < 2:
        logging.warning(
            "Priority labels have one or more classes with fewer than 2 samples; "
            "falling back to non-stratified train/test split."
        )
        stratify_pri = None
    else:
        stratify_pri = y_pri
    Xp_train, Xp_test, yp_train, yp_test = train_test_split(
        X_pri, y_pri, test_size=0.2, stratify=stratify_pri, random_state=42
    )
    best_pri_model, pri_results, pri_le = train_models(Xp_train, Xp_test, yp_train, yp_test, "priority")
    y_pri_pred = best_pri_model.predict(Xp_test)
    pri_report, pri_cm_file = evaluate_and_report(yp_test, y_pri_pred, labels=sorted(df["priority"].unique()), out_prefix=OUT_DIR / "priority")

    # Top misclassified examples
    test_df_cat = df.loc[idx_test]
    mis_cat = top_misclassified_examples(test_df_cat, yc_test.values, y_cat_pred, n=10)
    print("Top category misclassifications:")
    print(mis_cat.to_string(index=False))

    test_df_pri = df.loc[yp_test.index]
    mis_pri = top_misclassified_examples(test_df_pri, yp_test.values, y_pri_pred, n=10)
    print("Top priority misclassifications:")
    print(mis_pri.to_string(index=False))

    # Save models and artifacts
    joblib.dump(best_cat_model, OUT_DIR / "category_model.pkl")
    joblib.dump(best_pri_model, OUT_DIR / "priority_model.pkl")
    joblib.dump(vec, OUT_DIR / "tfidf_vectorizer.pkl")
    joblib.dump(cat_le, OUT_DIR / "category_label_encoder.pkl")
    joblib.dump(pri_le, OUT_DIR / "priority_label_encoder.pkl")

    print("Models and vectorizer saved to", OUT_DIR)
    print("Category confusion matrix:", cat_cm_file)
    print("Priority confusion matrix:", pri_cm_file)


if __name__ == "__main__":
    main()
