import sys, json, pymupdf
book_id, kw = sys.argv[1], sys.argv[2].lower()
m = {b["book_id"]: b for b in json.load(open("config/book_manifest.json", encoding="utf-8"))}
b = m[book_id]
print(f'{b["title"]} ({book_id}, {b["filename"]})')
doc = pymupdf.open("books/" + b["filename"])
hits = []
for i, page in enumerate(doc, 1):
    text = page.get_text()
    n = text.lower().count(kw)
    if n:
        hits.append((n, i, text))
for n, i, text in sorted(hits, reverse=True)[:8]:
    pos = text.lower().find(kw)
    snippet = " ".join(text[max(0, pos - 80):pos + 160].split())
    print(f'page {i}: {n} hits  {{"book_id": "{book_id}", "page": {i}}}')
    print("   ..." + snippet + "...")
