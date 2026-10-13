from support_rag.ingest import chunk_document, load_documents


def test_splits_by_heading():
    text = "# Title\n\nIntro line.\n\n## Billing\n\nRefunds within 14 days.\n\n## Security\n\nEnable 2FA."
    chunks = chunk_document(text, "doc.md")
    headings = [c.heading for c in chunks]
    assert "Billing" in headings
    assert "Security" in headings
    # heading text is prefixed onto the chunk body for retrieval context
    billing = next(c for c in chunks if c.heading == "Billing")
    assert "Refunds" in billing.text
    assert billing.chunk_id.startswith("doc.md#")


def test_length_split_with_overlap():
    body = " ".join(f"word{i}" for i in range(400))  # well over max_chars
    chunks = chunk_document(body, "big.txt", max_chars=200, overlap=50)
    assert len(chunks) > 1
    assert all(len(c.text) <= 220 for c in chunks)  # ~max_chars, allowing heading prefix
    # overlap: the tail of one chunk reappears at the start of the next
    assert chunks[0].text.split()[-1] in chunks[1].text


def test_html_headings_become_chunks():
    html = "<h1>FAQ</h1><h2>Trial</h2><p>14-day free trial.</p>"
    chunks = chunk_document(html, "faq.html")
    assert any("Trial" == c.heading for c in chunks)
    assert any("14-day free trial" in c.text for c in chunks)


def test_load_documents_reads_sample_docs():
    from pathlib import Path

    docs = Path(__file__).resolve().parent.parent / "sample_docs"
    chunks = load_documents(docs)
    sources = {c.source for c in chunks}
    # md, txt and html are all picked up
    assert {"billing.md", "troubleshooting.txt", "faq.html"} <= sources
    assert len(chunks) >= 10
