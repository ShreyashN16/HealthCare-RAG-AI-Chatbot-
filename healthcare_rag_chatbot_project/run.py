"""
Entry point for running the Healthcare RAG Chatbot locally.
Run from project root:  python run.py
"""
from chatbot.app import app

if __name__ == "__main__":
    print("=" * 50)
    print("  Healthcare RAG Chatbot")
    print("  http://127.0.0.1:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
