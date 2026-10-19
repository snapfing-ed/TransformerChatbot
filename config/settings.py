import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS_DIR = os.path.join(BASE_DIR, "books")  # where the PDFs actually are
DATA_DIR = os.path.join(BASE_DIR, "data")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
MANIFEST_PATH = os.path.join(BASE_DIR, "config", "book_manifest.json")
EVAL_QUESTIONS_PATH = os.path.join(BASE_DIR, "evaluation", "evaluation_questions.json")
REPORT_PATH = os.path.join(BASE_DIR, "evaluation", "report.json")

GROUP_ID = "G014"
SUBJECT = "Computer Science"

# Use the project-approved model; pin the exact commit hash once the coordinator confirms it.
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_REVISION = None  # e.g. "<commit hash from the model's HF page>"

# all-MiniLM-L6-v2 only reads ~256 tokens (~180 words). Longer chunks get silently truncated.
CHUNK_SIZE = 180      # words
CHUNK_OVERLAP = 30    # words
TOP_K = 5

# Abstention threshold on cosine similarity. MUST be tuned on the validation split, not guessed.
MIN_SCORE = 0.40
