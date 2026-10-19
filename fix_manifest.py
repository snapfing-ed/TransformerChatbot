import json, os
m = json.load(open("config/book_manifest.json", encoding="utf-8"))
files = [f for f in os.listdir("books") if f.lower().endswith(".pdf") and not f.startswith("130_")]
norm = lambda s: "".join(c for c in s.lower() if c.isalnum())
keys = {
    "G014_BOOK_004": "theoretical",
    "G014_BOOK_012": "networking",
    "G014_BOOK_013": "modeling",
    "G014_BOOK_014": "algorithmic",
    "G014_BOOK_015": "computerscienceone",
}
used = set()
for b in m:
    b["filename"] = ""
    k = keys.get(b["book_id"])
    if k:
        for f in files:
            if k in norm(f):
                b["filename"] = f
                used.add(f)
for b in m:
    print(b["book_id"], "->", b["filename"] or "NO PDF YET")
print("Unmatched files:", [f for f in files if f not in used])
json.dump(m, open("config/book_manifest.json", "w", encoding="utf-8"), indent=2)
