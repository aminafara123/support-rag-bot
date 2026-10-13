import os

# Force the deterministic, offline TF-IDF backend so tests never touch the network.
os.environ.setdefault("EMBED_BACKEND", "tfidf")
