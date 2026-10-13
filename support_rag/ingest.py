"""Load support docs and split them into overlapping, heading-aware chunks.

Supports .md/.txt/.html out of the box; .pdf is optional via pdfplumber.
"""
import html
import re
from dataclasses import dataclass
from pathlib import Path

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
SUPPORTED = (".md", ".markdown", ".txt", ".html", ".htm")


@dataclass
class Chunk:
    text: str       # chunk body (heading prefixed for context)
    source: str     # file name the chunk came from
    heading: str    # nearest heading, or "" if none
    chunk_id: str   # stable id like "billing.md#2"


def _html_to_md(text):
    # Turn <h1..6> into markdown headings so the same splitter handles HTML.
    text = re.sub(r"(?is)<\s*h[1-6][^>]*>(.*?)<\s*/\s*h[1-6]\s*>", r"\n\n## \1\n\n", text)
    text = re.sub(r"(?is)<\s*(script|style)[^>]*>.*?<\s*/\s*\1\s*>", "", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return html.unescape(text)


def _split_by_headings(text):
    sections, heading, buf = [], "", []
    for line in text.splitlines():
        m = HEADING_RE.match(line.strip())
        if m:
            if buf:
                sections.append((heading, "\n".join(buf).strip()))
                buf = []
            heading = m.group(2).strip()
        else:
            buf.append(line)
    if buf:
        sections.append((heading, "\n".join(buf).strip()))
    return [(h, b) for h, b in sections if b]


def _split_by_length(text, max_chars, overlap):
    text = text.strip()
    if len(text) <= max_chars:
        return [text] if text else []
    out, start, n = [], 0, len(text)
    while start < n:
        end = min(start + max_chars, n)
        if end < n:  # back off to a space so we don't cut a word
            ws = text.rfind(" ", start, end)
            if ws > start:
                end = ws
        out.append(text[start:end].strip())
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return [c for c in out if c]


def chunk_document(text, source, max_chars=800, overlap=150):
    """Split one document's text into Chunks, by heading then by length."""
    if source.lower().endswith((".html", ".htm")):
        text = _html_to_md(text)
    sections = _split_by_headings(text) or [("", text.strip())]
    chunks = []
    for heading, body in sections:
        for piece in _split_by_length(body, max_chars, overlap):
            chunks.append(
                Chunk(
                    text=f"{heading}\n{piece}" if heading else piece,
                    source=source,
                    heading=heading,
                    chunk_id=f"{source}#{len(chunks)}",
                )
            )
    return chunks


def _read_pdf(path):
    try:
        import pdfplumber
    except ImportError:
        return None
    with pdfplumber.open(path) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)


def load_documents(docs_dir, max_chars=800, overlap=150):
    """Read every supported file under docs_dir and return a flat list of Chunks."""
    chunks = []
    for path in sorted(Path(docs_dir).rglob("*")):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext in SUPPORTED:
            text = path.read_text(encoding="utf-8", errors="ignore")
        elif ext == ".pdf":
            text = _read_pdf(path)
            if text is None:
                continue  # pdfplumber not installed; skip silently
        else:
            continue
        chunks.extend(chunk_document(text, path.name, max_chars, overlap))
    return chunks
