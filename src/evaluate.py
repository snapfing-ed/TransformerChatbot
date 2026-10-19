"""Run the held-out evaluation and write evaluation/report.json with MEASURED numbers only.

evaluation_questions.json format (list of objects):
{
  "id": "Q001",
  "question": "What is a process?",
  "split": "validation" | "test",
  "answerable": true,
  "type": "direct | reasoning | numerical | cross-book | no-answer | citation-check",
  "expected_evidence": [{"book_id": "G014_BOOK_001", "page": 26}],
  "reference_answer": "...",
  "review_status": "reviewed" | "pending"
}
Run:  python -m src.evaluate --split validation
Only run --split test once, at the very end.
"""
import json
import time
import argparse
from config.settings import EVAL_QUESTIONS_PATH, REPORT_PATH, GROUP_ID, SUBJECT, TOP_K, MIN_SCORE
from src.retrieve import retrieve
from src.generate import generate_answer


def main(split):
    with open(EVAL_QUESTIONS_PATH, "r", encoding="utf-8") as f:
        qs = [q for q in json.load(f) if q["split"] == split and q.get("review_status") == "reviewed"]

    hits = n_ret = 0
    abst_ok = n_abst = 0
    cites_ok = n_cites = 0
    times = []
    failures = []

    for q in qs:
        t0 = time.time()
        res = generate_answer(q["question"])
        times.append(time.time() - t0)

        if q["answerable"]:
            n_ret += 1
            got = {(p["book_id"], p["page"]) for p in retrieve(q["question"], top_k=TOP_K)}
            want = {(e["book_id"], e["page"]) for e in q["expected_evidence"]}
            if got & want:
                hits += 1
            else:
                failures.append({"id": q["id"], "issue": "retrieval_miss"})
        else:
            n_abst += 1
            if res["insufficient_evidence"]:
                abst_ok += 1
            else:
                failures.append({"id": q["id"], "issue": "should_have_abstained"})

        for s in res["sources"]:  # citation traceability: does the source exist as a stored passage?
            n_cites += 1
            pid = s["chunk_id"]
            if any(p["chunk_id"] == pid for p in res["passages"]):
                cites_ok += 1

    report = {
        "group_id": GROUP_ID, "subject": SUBJECT, "split": split,
        "n_questions": len(qs),
        "settings": {"top_k": TOP_K, "min_score": MIN_SCORE},
        "metrics": {
            "retrieval_recall_at_5": hits / n_ret if n_ret else None,
            "abstention_accuracy": abst_ok / n_abst if n_abst else None,
            "citation_traceability": cites_ok / n_cites if n_cites else None,
            "avg_response_seconds": sum(times) / len(times) if times else None,
            "answer_correctness": None,  # fill in after human review
            "groundedness": None,        # fill in after human review
        },
        "failures": failures,
        "limitations": "TODO: write after error analysis.",
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report["metrics"], indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="validation", choices=["validation", "test"])
    main(ap.parse_args().split)