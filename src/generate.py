import os
import re
import json
import urllib.request
from src.retrieve import retrieve
from config.settings import MIN_SCORE, TOP_K

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL")  # e.g. "qwen2.5:3b"; unset = extractive mode
NO_EVIDENCE = ("The provided books do not contain sufficient evidence to answer this question.")


def _ollama_answer(question, passages):
    context = "\n\n".join(f"[{p['chunk_id']}] {p['text']}" for p in passages)
    prompt = (
        "Answer the question using ONLY the passages below. Cite passages by their [chunk_id]. "
        "Do not invent citations or facts. If the passages do not answer it, reply exactly: "
        "INSUFFICIENT_EVIDENCE\n\n" + context + f"\n\nQuestion: {question}\nAnswer:"
    )
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps({"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["response"].strip()


def generate_answer(question: str) -> dict:
    passages = retrieve(question, top_k=TOP_K)
    good = [p for p in passages if p["score"] >= MIN_SCORE]
    if not good:
        return {"answer": NO_EVIDENCE, "sources": [], "insufficient_evidence": True,
                "passages": passages}

    used = good[:3]
    answer = None
    if OLLAMA_MODEL:
        try:
            answer = _ollama_answer(question, used)
        except Exception:
            answer = None  # fall back to extractive mode; never block the baseline
    if answer is not None and "INSUFFICIENT_EVIDENCE" in answer:
        return {"answer": NO_EVIDENCE, "sources": [], "insufficient_evidence": True,
                "passages": passages}

    if answer is None:  # extractive baseline: show the best passage, honestly labelled
        answer = "Most relevant passage found in the books:\n\n" + used[0]["text"]
        cited_ids = {used[0]["chunk_id"]}
    else:  # keep only citations that map to real retrieved passages
        cited_ids = set(re.findall(r"\[([A-Za-z0-9_]+_P\d+_C\d+)\]", answer))
        cited_ids &= {p["chunk_id"] for p in used}
        if not cited_ids:
            cited_ids = {used[0]["chunk_id"]}

    sources = [{"book_id": p["book_id"], "page": p["page"], "chunk_id": p["chunk_id"]}
               for p in used if p["chunk_id"] in cited_ids]
    return {"answer": answer, "sources": sources, "insufficient_evidence": False,
            "passages": passages}