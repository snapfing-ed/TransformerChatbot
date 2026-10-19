import os
import re
import json
import pymupdf as fitz  # PyMuPDF (new import name; keeps the fitz alias used below)
from config.settings import (
    BOOKS_DIR, DATA_DIR, MANIFEST_PATH, GROUP_ID, SUBJECT, CHUNK_SIZE, CHUNK_OVERLAP,
)

MIN_CHARS_PER_PAGE = 50   # pages with less text are flagged (likely scanned/blank)
MIN_CHUNK_WORDS = 40      # drops tiny fragments (mostly overlap tails and stray captions)
MAX_FIGURE_REFS = 3       # drops list-of-figures / caption-heavy chunks


def chunk_words(words, size, overlap):
    step = size - overlap
    for i in range(0, len(words), step):
        piece = words[i:i + size]
        if piece:
            yield i // step, " ".join(piece)


def is_junk(chunk_text):
    if len(chunk_text.split()) < MIN_CHUNK_WORDS:
        return True
    return len(re.findall(r"Figure \d", chunk_text)) >= MAX_FIGURE_REFS


def extract_and_chunk_books():
    """Build passages.json from the manifest. Every passage carries real manifest metadata.

    Each manifest entry needs a "filename" field naming its PDF in the books/ folder.
    """
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    passages, report = [], {"books": [], "total_passages": 0}

    for book in manifest:
        entry = {"book_id": book["book_id"], "title": book["title"],
                 "pages": 0, "failed_pages": [], "dropped_chunks": 0, "status": "processed"}
        pdf_path = os.path.join(BOOKS_DIR, book.get("filename", ""))
        if not book.get("filename") or not os.path.exists(pdf_path):
            entry["status"] = "missing_pdf"
            report["books"].append(entry)
            continue

        doc = fitz.open(pdf_path)
        entry["pages"] = len(doc)
        for page_idx in range(len(doc)):
            text = doc[page_idx].get_text().strip()
            if len(text) < MIN_CHARS_PER_PAGE:
                entry["failed_pages"].append(page_idx + 1)
                continue
            for c, chunk_text in chunk_words(text.split(), CHUNK_SIZE, CHUNK_OVERLAP):
                if is_junk(chunk_text):
                    entry["dropped_chunks"] += 1
                    continue
                passages.append({
                    "group_id": GROUP_ID,
                    "subject": SUBJECT,
                    "book_id": book["book_id"],
                    "title": book["title"],
                    "edition": book["edition"],
                    "page": page_idx + 1,  # PDF page index, not necessarily the printed page number
                    "chunk_id": f"{book['book_id']}_P{page_idx + 1}_C{c:02d}",
                    "text": chunk_text,
                })
        report["books"].append(entry)

    report["total_passages"] = len(passages)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "passages.json"), "w", encoding="utf-8") as f:
        json.dump(passages, f, indent=2)
    with open(os.path.join(DATA_DIR, "ingestion_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return passages


if __name__ == "__main__":
    p = extract_and_chunk_books()
    print(f"Ingestion complete: {len(p)} passages. See data/ingestion_report.json")