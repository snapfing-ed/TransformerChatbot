import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS_DIR = os.path.join(BASE_DIR, 'books')
DATA_DIR = os.path.join(BASE_DIR, 'data')
ARTIFACTS_DIR = os.path.join(BASE_DIR, 'artifacts')

GROUP_ID = 'G014'
SUBJECT = 'Computer Science'
EMBEDDIND_MODEL = 'all-MiniLM-L6-v2'
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 5
