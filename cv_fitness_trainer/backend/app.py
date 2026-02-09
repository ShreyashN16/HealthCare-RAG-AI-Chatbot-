from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from tinydb import TinyDB
from datetime import datetime
import streaming
import json

app = Flask(__name__)
CORS(app)
db = TinyDB("analytics.json")

@app.route('/')
def index():
    return "Backend is running. Visit /video_feed for webcam."

@app.route('/video_feed')
def video_feed():
    return Response(streaming.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/metrics')
def get_metrics():
    return jsonify(streaming.get_current_metrics())

@app.route('/analytics', methods=['POST'])
def save_analytics():
    data = request.json or {}
    data["saved_at"] = datetime.utcnow().isoformat()
    doc_id = db.insert(data)
    streaming.rep_counter.reset()
    streaming.angles_history.clear()
    streaming.session_angles.clear()
    return jsonify({"status": "saved", "doc_id": doc_id}), 200

@app.route('/analytics', methods=['GET'])
def get_analytics():
    return jsonify(db.all()), 200

@app.route('/reset', methods=['POST'])
def reset_session():
    streaming.rep_counter.reset()
    streaming.angles_history.clear()
    streaming.session_angles.clear()
    streaming.angle_filter.reset()
    return jsonify({"status": "reset"}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
