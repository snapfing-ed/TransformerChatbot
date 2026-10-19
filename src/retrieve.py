import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from config.settings import DATA_DIR, EMBEDDING_MODEL, EMBEDDING_REVISION, TOP_K

PASSAGES_PATH = os.path.join(DATA_DIR, "passages.json")
INDEX_PATH = os.path.join(DATA_DIR, "index.faiss")
INDEX_META_PATH = os.path.join(DATA_DIR, "index_meta.json")


class Retriever:
    def __init__(self):
        if not os.path.exists(PASSAGES_PATH):
            from src.ingest import extract_and_chunk_books
            extract_and_chunk_books()
        with open(PASSAGES_PATH, "r", encoding="utf-8") as f:
            self.passages = json.load(f)

        self.model = SentenceTransformer(EMBEDDING_MODEL, revision=EMBEDDING_REVISION)
        meta = {"model": EMBEDDING_MODEL, "revision": EMBEDDING_REVISION,
                "n_passages": len(self.passages), "metric": "cosine (normalized inner product)"}

        if os.path.exists(INDEX_PATH) and os.path.exists(INDEX_META_PATH):
            with open(INDEX_META_PATH, "r", encoding="utf-8") as f:
                if json.load(f) == meta:
                    self.index = faiss.read_index(INDEX_PATH)
                    return

        print("Building index (one-time)...")
        texts = [p["text"] for p in self.passages]
        emb = self.model.encode(texts, batch_size=64, show_progress_bar=True,
                                normalize_embeddings=True).astype("float32")
        self.index = faiss.IndexFlatIP(emb.shape[1])
        self.index.add(emb)
        faiss.write_index(self.index, INDEX_PATH)
        with open(INDEX_META_PATH, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    def retrieve(self, question: str, top_k: int = TOP_K) -> list:
        """Return passages with text, score, book_id, title, page, and chunk_id."""
        q = self.model.encode([question], normalize_embeddings=True).astype("float32")
        scores, idxs = self.index.search(q, min(top_k, len(self.passages)))
        results = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx < 0:
                continue
            p = self.passages[idx].copy()
            p["score"] = float(score)  # cosine similarity in [-1, 1]
            results.append(p)
        return results


_retriever = None


def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


def retrieve(question: str, top_k: int = TOP_K) -> list:
    return get_retriever().retrieve(question, top_k)