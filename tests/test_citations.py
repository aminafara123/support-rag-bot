from support_rag.ingest import Chunk
from support_rag.rag import extract_citations

RETRIEVED = [
    (Chunk("Refunds within 14 days.", "billing.md", "Refunds", "billing.md#0"), 0.91),
    (Chunk("Enable 2FA.", "security.md", "2FA", "security.md#1"), 0.42),
    (Chunk("Slack alerts.", "integrations.md", "Slack", "integrations.md#2"), 0.30),
]


def test_extracts_used_citations_in_order():
    answer = "You can get a refund within 14 days [1], and you should enable 2FA [2]."
    cites = extract_citations(answer, RETRIEVED)
    assert [c["marker"] for c in cites] == [1, 2]
    assert cites[0]["source"] == "billing.md"
    assert cites[0]["chunk_id"] == "billing.md#0"
    assert cites[0]["heading"] == "Refunds"
    assert cites[0]["score"] == 0.91


def test_dedupes_and_ignores_out_of_range():
    answer = "See [2] and again [2]. Marker [9] does not exist."
    cites = extract_citations(answer, RETRIEVED)
    assert [c["marker"] for c in cites] == [2]


def test_no_markers_returns_empty():
    assert extract_citations("I don't know; please contact support.", RETRIEVED) == []
