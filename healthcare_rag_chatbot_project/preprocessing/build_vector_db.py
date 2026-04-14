
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

model = SentenceTransformer("all-MiniLM-L6-v2")

with open("data/chunks.txt",encoding="utf-8") as f:
    docs = f.read().split("\n\n")

embeddings = model.encode(docs)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

faiss.write_index(index,"vector_db.index")

pickle.dump(docs,open("docs.pkl","wb"))

print("Vector database created.")
