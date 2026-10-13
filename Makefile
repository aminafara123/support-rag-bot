PY ?= python3
VENV = .venv
BIN = $(VENV)/bin

.PHONY: install test run clean

install:
	$(PY) -m venv $(VENV)
	$(BIN)/pip install -U pip
	$(BIN)/pip install -r requirements.txt

test:
	$(BIN)/pytest -q

run:
	$(BIN)/uvicorn support_rag.server:app --host 0.0.0.0 --port 8000

clean:
	rm -rf $(VENV) .pytest_cache **/__pycache__
