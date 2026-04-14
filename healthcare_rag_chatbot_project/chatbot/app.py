import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify, send_from_directory
from chatbot.rag_engine import search

# Resolve UI folder
_UI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui")

app = Flask(__name__, static_folder=_UI_DIR, static_url_path="/")


PORT = int(os.getenv("APP_PORT", 5000))
DEBUG = os.getenv("FLASK_ENV") != "production"

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    if not data or "question" not in data:
        return jsonify({"error": "Missing 'question' field"}), 400

    question = data["question"]
    answer = search(question)
    return jsonify({"answer": answer})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)