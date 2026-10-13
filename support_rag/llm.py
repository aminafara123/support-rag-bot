"""Thin OpenAI-compatible LLM client (chat + embeddings).

Configured only by env; defaults target a local ollama. No key is ever hardcoded.
Both calls raise LLMUnavailable on any network/HTTP/parse error so callers can
degrade gracefully instead of crashing. Uses stdlib urllib (no extra dependency).
"""
import json
import os
import urllib.error
import urllib.request

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3:30b-a3b-instruct-2507-q4_K_M")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")


class LLMUnavailable(RuntimeError):
    """The LLM endpoint could not be reached or returned something unusable."""


def _post(path, payload, timeout):
    req = urllib.request.Request(
        f"{LLM_BASE_URL}{path}",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise LLMUnavailable(str(e)) from e


def chat(messages, temperature=0.0, timeout=60):
    """Return the assistant's reply text for a list of chat messages."""
    body = _post(
        "/chat/completions",
        {"model": LLM_MODEL, "messages": messages, "temperature": temperature, "stream": False},
        timeout,
    )
    try:
        return body["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as e:
        raise LLMUnavailable(f"unexpected chat response: {e}") from e


def embed_texts(texts, timeout=60):
    """Return one embedding vector per input text."""
    body = _post("/embeddings", {"model": EMBED_MODEL, "input": list(texts)}, timeout)
    try:
        return [d["embedding"] for d in body["data"]]
    except (KeyError, TypeError) as e:
        raise LLMUnavailable(f"unexpected embeddings response: {e}") from e
