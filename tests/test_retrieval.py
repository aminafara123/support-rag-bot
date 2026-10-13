import pytest

from support_rag import llm
from support_rag.ingest import Chunk
from support_rag.index import Retriever

CHUNKS = [
    Chunk("How to reset your password: use the forgot password link.", "security.md", "Reset", "security.md#0"),
    Chunk("Refunds are available within 14 days of your first payment.", "billing.md", "Refunds", "billing.md#0"),
    Chunk("Enable two-factor authentication with an authenticator app.", "security.md", "2FA", "security.md#1"),
]


def test_tfidf_ranks_relevant_chunk_first():
    r = Retriever(CHUNKS, backend="tfidf")
    top = r.query("how do refunds work?", k=2)
    assert r.backend == "tfidf"
    assert top[0][0].chunk_id == "billing.md#0"
    # scores are sorted descending
    assert top[0][1] >= top[1][1]


def test_k_caps_at_corpus_size():
    r = Retriever(CHUNKS, backend="tfidf")
    assert len(r.query("password", k=10)) == len(CHUNKS)


def test_auto_falls_back_to_tfidf_when_embeddings_unavailable(monkeypatch):
    def boom(_texts, timeout=60):
        raise llm.LLMUnavailable("no endpoint")

    monkeypatch.setattr(llm, "embed_texts", boom)
    r = Retriever(CHUNKS, backend="auto")
    assert r.backend == "tfidf"
    assert r.query("two factor", k=1)[0][0].chunk_id == "security.md#1"


def test_remote_backend_raises_without_endpoint(monkeypatch):
    def boom(_texts, timeout=60):
        raise llm.LLMUnavailable("no endpoint")

    monkeypatch.setattr(llm, "embed_texts", boom)
    with pytest.raises(llm.LLMUnavailable):
        Retriever(CHUNKS, backend="remote")
