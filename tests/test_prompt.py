from support_rag.ingest import Chunk
from support_rag.rag import SYSTEM_PROMPT, build_prompt

RETRIEVED = [
    (Chunk("Refunds within 14 days.", "billing.md", "Refunds", "billing.md#0"), 0.9),
    (Chunk("Enable 2FA in settings.", "security.md", "2FA", "security.md#1"), 0.5),
]


def test_prompt_is_grounded_and_numbered():
    messages = build_prompt("How do refunds work?", RETRIEVED)
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == SYSTEM_PROMPT
    user = messages[1]["content"]
    # context is numbered and source-tagged
    assert "[1] (source: billing.md#0)" in user
    assert "[2] (source: security.md#1)" in user
    assert "Refunds within 14 days." in user
    # the question and the grounding instruction are present
    assert "How do refunds work?" in user
    assert "only the context" in user.lower()


def test_prompt_handles_no_results():
    messages = build_prompt("anything", [])
    assert "(no documents found)" in messages[1]["content"]
