# 60-second demo script

Goal: show docs in -> grounded, cited answer out, in the terminal and the widget.

## Setup (before recording)

```bash
make install
# optional, for real LLM answers:
#   ollama serve &  and  ollama pull nomic-embed-text  +  a chat model
```

## Recording (~60s)

1) **Show the tests pass offline (0:00-0:12)**
   ```bash
   make test
   ```
   Point at the green summary line: everything runs with no network, no API key.

2) **Show the sample docs (0:12-0:20)**
   ```bash
   ls sample_docs/
   ```
   Say: "These are the client's help docs. The bot only answers from these."

3) **Hit the API (0:20-0:38)**
   ```bash
   make run        # in one pane
   ```
   ```bash
   curl -s localhost:8000/chat -H 'content-type: application/json' \
     -d '{"question":"How do I get a refund?"}' | jq
   ```
   Highlight the `answer`, the `citations` (source doc + chunk), and the `disclaimer`.

4) **Show grounding / honesty (0:38-0:48)**
   ```bash
   curl -s localhost:8000/chat -H 'content-type: application/json' \
     -d '{"question":"Do you support Salesforce?"}' | jq .answer
   ```
   Say: "Not in the docs, so it says it doesn't know instead of hallucinating."

5) **Open the widget (0:48-0:60)**
   Open <http://localhost:8000>, type "How do I enable 2FA?", show the answer with
   its "Sources:" line. Mention it embeds anywhere via a one-line iframe.
