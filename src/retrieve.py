import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from config.settings import DATA_DIR, EMBEDDING_MODEL, TOP_K

class Retriever:
    def __init__(self):
        passages_path = os.path.join(DATA_DIR, "passages.json")
        if not os.path.exists(passages_path):
            from src.ingest import extract_and_chunk_books
            extract_and_chunk_books()
            
        with open(passages_path, "r", encoding="utf-8") as f:
            self.passages = json.load(f)
            
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        texts = [p["text"] for p in self.passages]
        
        print("Embedding passages for vector search...")
        embeddings = self.model.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings).astype("float32")
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

    def retrieve(self, question: str, top_k: int = TOP_K) -> list:
        """Return passages with text, score, book_id, title, page, and chunk_id."""
        query_vector = self.model.encode([question]).astype("float32")
        distances, indices = self.index.search(query_vector, min(top_k, len(self.passages)))
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.passages):
                p = self.passages[idx].copy()
                p["score"] = float(1.0 / (1.0 + dist))  # Convert L2 distance to similarity score
                results.append(p)
        return results

# Global retriever instance
_retriever = None

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever

def retrieve(question: str, top_k: int = TOP_K) -> list:
    retriever = get_retriever()
    return retriever.retrieve(question, top_k)