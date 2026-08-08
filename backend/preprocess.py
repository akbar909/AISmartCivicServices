import re
from typing import List
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Ensure required NLTK data is present. The training script will call download when needed,
# but leaving this import here keeps preprocessing self-contained when resources exist.
_STOPWORDS = set()
_LEMMATIZER = WordNetLemmatizer()


def ensure_nltk_resources():
    try:
        nltk.data.find("corpora/wordnet")
    except Exception:
        nltk.download("wordnet")
    try:
        nltk.data.find("corpora/omw-1.4")
    except Exception:
        nltk.download("omw-1.4")
    try:
        nltk.data.find("corpora/stopwords")
    except Exception:
        nltk.download("stopwords")


def _init_stopwords():
    global _STOPWORDS
    if not _STOPWORDS:
        english = set(stopwords.words("english"))
        # Keep negation words which are important for polarity/intent
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


def lemmatize_tokens(tokens: List[str]) -> List[str]:
    return [_LEMMATIZER.lemmatize(tok) for tok in tokens]


def preprocess_text(text: str) -> str:
    """Full preprocessing pipeline used at train and inference time.

    Steps:
    - Lowercase and basic cleaning
    - Tokenize on whitespace
    - Remove stopwords (but keep negations)
    - Lemmatize tokens
    - Return cleaned string (tokens joined)
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


if __name__ == "__main__":
    # quick manual test
    print(preprocess_text("Pothole on 5th Ave causing car damage. Not fixed!"))
