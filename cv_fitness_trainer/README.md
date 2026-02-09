# CV Fitness Trainer

A computer vision-based fitness trainer application that uses MediaPipe pose detection to analyze exercise form, count reps, and provide real-time feedback.

## Features

- **Real-time Pose Detection**: Uses MediaPipe to detect and track body landmarks
- **Rep Counting**: State machine-based rep counting with configurable thresholds
- **Form Analysis**: Symmetry detection, torso tilt detection, ROM calculation, and tempo analysis
- **Analytics Dashboard**: Track workout sessions with visual charts and statistics
- **Live Video Streaming**: MJPEG video stream from webcam
- **RESTful API**: Flask backend with endpoints for video streaming and analytics

## Project Structure

```
cv_fitness_trainer/
├── backend/
│   ├── app.py                 # Flask application with routes
│   ├── pose_detection.py      # MediaPipe pose detection wrapper
│   ├── angle_math.py          # Vector and angle calculations
│   ├── rep_logic.py           # Rep counting state machine
│   ├── form_feedback.py       # Form analysis functions
│   ├── analytics.py           # TinyDB storage for metrics
│   ├── streaming.py           # OpenCV video capture generator
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── index.html            # Main training interface
│   ├── dashboard.html        # Analytics dashboard
│   ├── style.css             # Styling
│   └── script.js             # Frontend JavaScript
└── README.md                 # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Webcam/camera device
- Modern web browser

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note**: You may also need to install Flask-CORS if not included:
```bash
pip install flask-cors
```

## Running the Application

### Start the Backend Server

From the `backend` directory:

```bash
python app.py
```

The Flask server will start on `http://localhost:5000`.

### View the Frontend

Open `frontend/index.html` in your web browser. You can:

1. Double-click the file to open it in your default browser
2. Or use a local web server:
   ```bash
   cd frontend
   python -m http.server 8000
   ```
   Then navigate to `http://localhost:8000/index.html`

**Note**: If opening directly from the file system, you may encounter CORS issues. For production use, serve the frontend through a web server or configure Flask to serve static files.

## Architecture Overview

### Backend Components

1. **Pose Detection** (`pose_detection.py`): Wraps MediaPipe pose detection, processes BGR frames, and returns landmarks with annotated output.

2. **Angle Math** (`angle_math.py`): Provides utilities for vector calculations, angle computation using dot products, and moving average filtering for smoothing.

3. **Rep Logic** (`rep_logic.py`): Implements a state machine with states (REST, UP, PEAK, DOWN, REP_DONE) and configurable angle thresholds for rep counting.

4. **Form Feedback** (`form_feedback.py`): Analyzes exercise form through:
   - Symmetry detection (left vs right side comparison)
   - Torso tilt detection
   - Range of motion (ROM) calculation
   - Tempo calculation for ascending/descending phases

5. **Streaming** (`streaming.py`): OpenCV-based video capture that yields MJPEG frames for Flask streaming.

6. **Analytics** (`analytics.py`): TinyDB storage for session metrics including timestamp, exercise type, valid reps, symmetry scores, ROM, and tempo data.

7. **Flask App** (`app.py`): Provides three main routes:
   - `/video_feed`: MJPEG video stream endpoint
   - `/analytics` (POST): Save session metrics
   - `/analytics` (GET): Retrieve stored analytics

### Frontend Components

1. **Main Interface** (`index.html`): Displays live video stream, rep counter, form feedback indicators, and session controls.

2. **Dashboard** (`dashboard.html`): Analytics visualization using Chart.js with multiple charts for reps, symmetry, ROM, and tempo analysis.

3. **Styling** (`style.css`): Modern, responsive CSS with gradient backgrounds and card-based layouts.

4. **JavaScript** (`script.js`): Handles UI updates, API communication, and session management.

## API Endpoints

### GET /video_feed
Returns MJPEG video stream from the webcam.

### POST /analytics
Save a training session to the database.

**Request Body:**
```json
{
  "exercise": "squat",
  "valid_reps": 10,
  "symmetry_score": 85.5,
  "rom": 120.0,
  "tempo_up": 0.5,
  "tempo_down": 0.8
}
```

### GET /analytics
Retrieve stored analytics data.

**Query Parameters:**
- `exercise` (optional): Filter by exercise name
- `limit` (optional): Limit number of results

**Response:**
```json
{
  "sessions": [
    {
      "timestamp": "2024-01-01T12:00:00",
      "exercise": "squat",
      "valid_reps": 10,
      "symmetry_score": 85.5,
      "rom": 120.0,
      "tempo_up": 0.5,
      "tempo_down": 0.8
    }
  ]
}
```

### GET /health
Health check endpoint returning status.

## Usage Tips

1. Ensure good lighting and clear camera view of the user
2. Stand at a distance where your full body is visible
3. Adjust rep counting thresholds in `rep_logic.py` if needed for different exercises
4. The analytics database is stored as `analytics.json` in the backend directory
5. For best results, calibrate angle thresholds based on your exercise form

## Troubleshooting

- **Camera not working**: Check camera permissions and ensure no other application is using the camera
- **CORS errors**: Make sure Flask-CORS is installed and the backend is running
- **No pose detection**: Ensure good lighting and full body visibility in the camera frame
- **Import errors**: Verify all dependencies are installed with `pip install -r requirements.txt`

## Future Enhancements

- Integration of pose detection into the main training flow
- Real-time angle calculation and rep counting on video stream
- Exercise-specific form analysis presets
- User authentication and session management
- Export analytics data to CSV/JSON

## License

This project is provided as-is for educational and personal use.
