"""FastAPI app: POST /chat (question -> answer + citations) and a chat widget at /."""
import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from . import ingest, rag
from .index import Retriever

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = Path(os.getenv("DOCS_DIR", ROOT / "sample_docs"))
WIDGET = ROOT / "static" / "widget.html"

app = FastAPI(title="Support RAG Bot")


@lru_cache(maxsize=1)
def get_retriever():
    return Retriever(ingest.load_documents(DOCS_DIR))


class ChatRequest(BaseModel):
    question: str


class Citation(BaseModel):
    marker: int
    source: str
    chunk_id: str
    heading: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    disclaimer: str


@app.get("/", response_class=HTMLResponse)
def widget():
    return WIDGET.read_text(encoding="utf-8")


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    q = req.question.strip()
    if not q:
        return {"answer": "Please enter a question.", "citations": [], "disclaimer": rag.DISCLAIMER}
    return rag.answer(q, get_retriever())


def main():
    """Console entry point: serve the app with uvicorn (HOST/PORT from env)."""
    import uvicorn

    uvicorn.run(
        "support_rag.server:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
    )


if __name__ == "__main__":
    main()
