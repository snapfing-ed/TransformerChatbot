# Collaborative Transformer Chatbot — starter

A local Windows RAG prototype using PyMuPDF, Sentence Transformers, NumPy cosine similarity, and Streamlit. It does not train a Transformer. It preserves page-level metadata and provides an honest retrieval-only fallback if a generative model is not configured.

## Setup (PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

If `py -3.11` is unavailable, install Python 3.11 or replace it with an installed supported version (e.g. `py -3.12`).

## Add books
Put permitted PDFs in `books\`. Fill `book_manifest.csv` with accurate metadata and exact PDF filenames. One row per book; use unique group-level book IDs. Never invent metadata or permissions.

## Build the index
Start the app and click **Build / rebuild knowledge base**, or use the sidebar workflow after completing the manifest. First run downloads the pinned embedding model and needs internet. Review `data/ingestion_report.json`. Scanned PDFs may require OCR; do not count missing/failed books as processed.

## Optional local generation
By default the app shows retrieved source passages without pretending to synthesize a response. If Ollama is installed, a suitable model is downloaded, and Ollama is running, set a model name before launching, e.g.:
```powershell
$env:OLLAMA_MODEL="qwen2.5:3b"
python -m streamlit run app.py
```
Check the actual model name with `ollama list`. A 3B quantized model can still be slow on 8 GB RAM; don't let it block the retrieval baseline.

## Evaluation
Build a reviewed set of answerable, reasoning, cross-book, technical, and no-answer questions. Keep final test questions separate from prompt/model tuning. Measure retrieval Recall@5, answer correctness, citation correctness, abstention, latency, RAM, and known failures. Citation IDs resolving to chunks does not prove the chunks support the claims; review support manually.

Do not upload restricted PDFs, extracted full text, credentials, or personal data to public repositories. Record the legal basis for processing and sharing each source.
