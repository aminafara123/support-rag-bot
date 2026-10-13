"""Pluggable embedder + cosine top-k retrieval.

Default backend ("auto") tries the LLM provider's embeddings endpoint and, if it
is unavailable, falls back automatically to a deterministic scikit-learn TF-IDF
index -- so retrieval works fully offline (and all tests run with no network).
"""
import os

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from . import llm


def _l2(matrix):
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


class Retriever:
    def __init__(self, chunks, backend=None):
        self.chunks = list(chunks)
        texts = [c.text for c in self.chunks]
        backend = backend or os.getenv("EMBED_BACKEND", "auto")

        if texts and backend in ("auto", "remote"):
            try:
                self._matrix = _l2(np.asarray(llm.embed_texts(texts), dtype=float))
                self.backend = "remote"
                return
            except llm.LLMUnavailable:
                if backend == "remote":
                    raise
                # auto: fall through to the offline TF-IDF index

        # TfidfVectorizer L2-normalizes rows, so a dot product is cosine similarity.
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform(texts) if texts else None
        self.backend = "tfidf"

    def query(self, question, k=4):
        """Return the k most similar chunks as (chunk, cosine_score) pairs."""
        if not self.chunks:
            return []
        if self.backend == "remote":
            qv = _l2(np.asarray(llm.embed_texts([question]), dtype=float))[0]
            sims = self._matrix @ qv
        else:
            qv = self._vectorizer.transform([question])
            sims = (self._matrix @ qv.T).toarray().ravel()
        k = min(k, len(self.chunks))
        order = np.argsort(-sims)[:k]
        return [(self.chunks[i], float(sims[i])) for i in order]
