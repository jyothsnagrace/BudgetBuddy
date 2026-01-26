# Budget Buddy — Course Project

Budget Buddy is a small prototype LLM-powered personal finance assistant for a DSBA masters course project. It demonstrates:

- ingesting user finance data
- storing/retrieving contextual documents in a vector store
- wrapping an LLM (OpenAI) with system prompts to generate a budget plan and suggestions
- providing a creative output based on the plan

This repository provides a minimal FastAPI backend, a FAISS-based vector store (using SentenceTransformers), a small LLM wrapper with a fallback, and pytest tests.

Warning: some packages (faiss-cpu, sentence-transformers) may require a compatible Python environment and native dependencies.

Quick start (Windows PowerShell):

1. Create a virtual env and activate it

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Copy environment variables

```powershell
copy .env.example .env
# then edit .env to add OPENAI_API_KEY if you want real LLM calls
```

4. Run tests

```powershell
python -m pytest -q
```

5. Run server

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Endpoints:
- POST /ingest — add user finance data (JSON) into the vector store
- POST /plan — generate a budget plan using stored data and the LLM wrapper
- POST /creative — produce a creative output (e.g., a friendly letter summarizing the plan)

Files of interest:
- `app/main.py` — FastAPI app
- `app/vectorstore.py` — small FAISS wrapper
- `app/llm.py` — LLM wrapper (OpenAI + fallback)
- `prompts/system_prompt.txt` — main system prompt used for budgeting
- `tests/test_api.py` — basic API tests

Next steps / ideas:
- Persist vector store to disk or use a hosted vector DB (Pinecone / Chroma / Weaviate)
 - Persist vector store to disk or use a hosted vector DB (Pinecone / Chroma / Weaviate)
 - Structured JSON output: the LLM is asked to return a JSON budget plan; the code falls back to a heuristic structured plan when OpenAI is not available.

Optional higher-quality embeddings
- By default the project uses a TF-IDF fallback (scikit-learn) for small demos and portability.
- If you want higher-quality embeddings and faster NN search, install `sentence-transformers` and `faiss-cpu` in your environment. Example:

```powershell
# optional: install heavy dependencies for better embeddings (may require build tools)
& ".\.venv\Scripts\python.exe" -m pip install sentence-transformers faiss-cpu
```

Persistence
- The vector store supports `save(path)` and `load(path)` (see `app/vectorstore.py`) which will persist metadatas and the index/docs depending on the backend.

Notes on LLM behavior
- Set `OPENAI_API_KEY` in `.env` to enable real OpenAI calls. Without a key the project uses a deterministic fallback so the demo works offline.
- Add authentication + per-user storage
- Create a React/Streamlit UI for interactive flows
- Add deeper financial logic and risk checks
