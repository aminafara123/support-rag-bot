"""Grounded prompt assembly, citation extraction, and the answer orchestration."""
import re

from . import llm

SYSTEM_PROMPT = (
    "You are Nimbus's customer-support assistant. "
    "Answer ONLY using the provided context. "
    "If the answer is not in the context, say you don't know and suggest contacting support. "
    "Cite the sources you use with their bracket numbers, e.g. [1], [2]."
)

DISCLAIMER = (
    "AI-generated from Nimbus support docs. Verify important details; "
    "a human should review before acting on this answer."
)

CITATION_RE = re.compile(r"\[(\d+)\]")


def build_prompt(question, retrieved):
    """Build the [system, user] messages with numbered, source-tagged context."""
    blocks = [
        f"[{i}] (source: {chunk.chunk_id})\n{chunk.text}"
        for i, (chunk, _score) in enumerate(retrieved, 1)
    ]
    context = "\n\n".join(blocks) if blocks else "(no documents found)"
    user = (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the context above and cite the sources you use like [1]. "
        "If the context does not contain the answer, say you don't know."
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def extract_citations(answer_text, retrieved):
    """Map the [n] markers the model used back to their source chunks (deduped, in order)."""
    seen = {}
    for m in CITATION_RE.finditer(answer_text):
        n = int(m.group(1))
        if 1 <= n <= len(retrieved) and n not in seen:
            chunk, score = retrieved[n - 1]
            seen[n] = {
                "marker": n,
                "source": chunk.source,
                "chunk_id": chunk.chunk_id,
                "heading": chunk.heading,
                "score": round(score, 4),
            }
    return [seen[n] for n in sorted(seen)]


def answer(question, retriever, k=4, chat_fn=None):
    """Retrieve, ground, call the LLM, and return {answer, citations, disclaimer}."""
    chat_fn = chat_fn or llm.chat
    retrieved = retriever.query(question, k=k)
    messages = build_prompt(question, retrieved)
    try:
        text = chat_fn(messages)
    except llm.LLMUnavailable as e:
        # Degrade: no model, but still hand back the most relevant sources.
        text = (
            "I can't reach the language model right now, so I can only point you to the "
            f"most relevant docs below (details: {e})."
        )
        text += " " + " ".join(f"[{i}]" for i in range(1, len(retrieved) + 1))
    return {
        "answer": text,
        "citations": extract_citations(text, retrieved),
        "disclaimer": DISCLAIMER,
    }
