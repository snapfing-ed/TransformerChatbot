import json
p = "config/book_manifest.json"
m = json.load(open(p, encoding="utf-8"))
if not any(b["book_id"] == "G014_BOOK_016" for b in m):
    m.append({"book_id": "G014_BOOK_016", "title": "Python for Everybody: Exploring Data Using Python 3", "author": "Charles R. Severance", "edition": "VERIFY (title page)", "publisher": "VERIFY", "year": "VERIFY", "isbn": "N/A", "subject": "Computer Science", "source_type": "PDF text", "permission_status": "Open license (CC BY) - VERIFY", "processing_status": "pending", "filename": "python_for_everybody.pdf"})
json.dump(m, open(p, "w", encoding="utf-8"), indent=2)
print(len(m), "books in manifest")
