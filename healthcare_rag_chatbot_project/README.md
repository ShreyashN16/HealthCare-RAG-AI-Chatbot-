# 🏥 Healthcare RAG Chatbot

An AI-powered, medical knowledge chatbot built using **Retrieval-Augmented Generation (RAG)**. This project ingests healthcare documents (e.g., medical books in PDF format), processes them into vector embeddings, and uses a Language Model to provide accurate, context-aware answers to user queries.

It is designed for speed and reliability, featuring a lightweight **CPU-only inference pipeline** and a **production-ready backend containerized with Docker**.

---

## 🧠 AI / ML Architecture

This application employs a lightweight RAG architecture optimized for typical hardware (No GPUs required).

### 1. The RAG Pipeline
* **Embeddings:** Uses `sentence-transformers` (`all-MiniLM-L6-v2`) to convert medical text chunks and user queries into dense numerical vectors.
* **Vector Database:** Uses **FAISS** (Facebook AI Similarity Search) to index these embeddings. FAISS enables blazing-fast nearest-neighbor searches to find the most relevant document chunks for a given query.
* **Retrieval & Context:** When a user asks a question, the query is vectorized, compared against the FAISS index, and the top-K relevant chunks are returned as context to build an answer.

### 2. Preprocessing Flow
Before the chatbot can answer questions, raw documents must be processed.
1. **Extraction:** (`preprocessing/extract_text.py`) Reads PDFs via `pdfplumber` to extract raw text.
2. **Chunking:** (`preprocessing/chunk_text.py`) Breaks large extracted text into manageable chunks so the embeddings maintain specific, granular context.
3. **Indexing:** (`preprocessing/build_vector_db.py`) Converts chunks into vectors via `sentence-transformers` and saves the `vector_db.index` (for FAISS) and `docs.pkl` (for textual reference).

---

## 🛠 Tech Stack

* **Backend:** Python 3.12+, Flask, Gunicorn
* **AI/ML:** PyTorch (CPU-only), Sentence-transformers, FAISS
* **Frontend:** Vanilla HTML, CSS, JavaScript (served via Flask)
* **Infrastructure:** Docker (Multi-stage builds)

---

## 🐳 Docker Deployment (Production)

The project includes a highly optimized, production-ready `Dockerfile`.

### Docker Architecture
* **Multi-Stage Build:** 
  * **Stage 1 (Builder):** Installs heavy build dependencies (`build-essential`, `libgomp1`), creates a virtual environment, and installs Python packages.
  * **Stage 2 (Runtime):** A minimal `python:3.10-slim` image that only copies the compiled virtual environment and app source code. No dev tools or temporary files are included, keeping the image size drastically smaller.
* **Security First:** Runs as a non-root user (`appuser`).
* **Process Management:** Uses `tini` as the init process for graceful shutdowns and zombie process reaping.
* **Server:** Uses `gunicorn` (Production WSGI server) instead of Flask's built-in dev server.

### Running with Docker

1. **Build the image:**
   ```bash
   docker build -t healthcare-rag .
   ```
2. **Run the container:**
   ```bash
   docker run -d -p 5000:5000 --name rag-chatbot healthcare-rag
   ```
3. **Access the Chatbot:**
   Open http://localhost:5000 in your browser.

---

## 💻 Local Development (Windows / CPU-only)

If you wish to run the project locally without Docker, follow these steps to set up a clean, CPU-optimized environment.

### 1. Setup Virtual Environment
Always use a virtual environment to prevent package conflicts. Run from the project root:
```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
This project is explicitly configured to install **CPU-only** PyTorch, making installation much faster and preventing massive GPU library downloads on systems without CUDA.

```powershell
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
```

### 3. Run the Preprocessing Pipeline *(If starting from scratch)*
If you add new PDFs to the `data/` folder, run the pipeline to rebuild the FAISS index:
```bash
python preprocessing/extract_text.py
python preprocessing/chunk_text.py
python preprocessing/build_vector_db.py
```

### 4. Run the App
Start the local server using the main entry point script:
```powershell
python run.py
```

Open http://127.0.0.1:5000 in your browser.

---

## 📂 Project Structure

```
healthcare_rag_chatbot_project/
├── .venv/                  # Virtual environment
├── chatbot/                # Core application module
│   ├── __init__.py         
│   ├── app.py              # Flask server and API endpoints
│   └── rag_engine.py       # FAISS query and embedding generation
├── data/                   # Source documents (PDFs)
├── preprocessing/          # Data ingestion scripts
├── ui/                     # Frontend static assets
│   ├── index.html
│   ├── script.js
│   └── style.css
├── docs.pkl                # Pickled document store
├── vector_db.index         # Compiled FAISS index
├── requirements.txt        # CPU-only dependencies
├── run.py                  # Entry point for local execution
└── Dockerfile              # Production container blueprint
```
