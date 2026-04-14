import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# Resolve paths relative to the project root (one level up from this file)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_INDEX_PATH = os.path.join(_PROJECT_ROOT, "vector_db.index")
_DOCS_PATH = os.path.join(_PROJECT_ROOT, "docs.pkl")

# Load the embedding model (CPU-only)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index and document store
index = faiss.read_index(_INDEX_PATH)
with open(_DOCS_PATH, "rb") as f:
    docs = pickle.load(f)


def search(query: str, top_k: int = 3) -> str:
    """Search the FAISS index for the most relevant documents."""
    query_vector = model.encode([query]).astype(np.float32)
    _distances, indices = index.search(query_vector, top_k)
    results = [docs[i] for i in indices[0] if i < len(docs)]
    return " ".join(results)
