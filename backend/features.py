from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Optional
import logging


def build_tfidf(corpus, max_features: int = 8000, min_df: int = 2):
    """Create and fit a TF-IDF vectorizer (unigrams + bigrams).

    Returns fitted vectorizer and transformed matrix.
    """
    vec = TfidfVectorizer(ngram_range=(1, 2), max_features=max_features, min_df=min_df)
    X = vec.fit_transform(corpus)
    logging.info("TF-IDF vectorizer fitted: vocab=%d", len(vec.vocabulary_))
    return vec, X


def try_sentence_embeddings(corpus, model_name: str = "all-MiniLM-L6-v2"):
    try:
        from sentence_transformers import SentenceTransformer
    except Exception:
        raise
    model = SentenceTransformer(model_name)
    embeddings = model.encode(corpus, show_progress_bar=True)
    return model, embeddings
