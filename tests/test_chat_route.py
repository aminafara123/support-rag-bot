from fastapi.testclient import TestClient

from support_rag import llm, server


def _client(monkeypatch, fake_chat):
    monkeypatch.setattr(llm, "chat", fake_chat)
    server.get_retriever.cache_clear()  # rebuild the (TF-IDF) index fresh per test
    return TestClient(server.app)


def test_chat_returns_answer_and_citations(monkeypatch):
    # Mocked LLM: echoes a grounded-looking answer that cites source [1].
    captured = {}

    def fake_chat(messages, **kw):
        captured["messages"] = messages
        return "You can request a refund within 14 days of your first payment [1]."

    client = _client(monkeypatch, fake_chat)
    resp = client.post("/chat", json={"question": "How do I get a refund?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "refund" in data["answer"].lower()
    assert data["citations"], "expected at least one citation"
    assert data["citations"][0]["marker"] == 1
    assert data["citations"][0]["source"].endswith((".md", ".txt", ".html"))
    assert "AI-generated" in data["disclaimer"]
    # the prompt actually carried retrieved context to the model
    assert "Context:" in captured["messages"][1]["content"]


def test_chat_degrades_when_llm_unavailable(monkeypatch):
    def boom(messages, **kw):
        raise llm.LLMUnavailable("connection refused")

    client = _client(monkeypatch, boom)
    resp = client.post("/chat", json={"question": "How do I reset my password?"})
    assert resp.status_code == 200
    data = resp.json()
    # still returns sources even though the model is down, and never 500s
    assert data["citations"]
    assert "can't reach the language model" in data["answer"]


def test_empty_question_is_handled(monkeypatch):
    client = _client(monkeypatch, lambda *a, **k: "unused")
    resp = client.post("/chat", json={"question": "   "})
    assert resp.status_code == 200
    assert resp.json()["citations"] == []
