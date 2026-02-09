import cv2
import numpy as np
from pose_detection import PoseDetector
from angle_math import calculate_angle_from_points, MovingAverageFilter
from rep_logic import RepCounter, RepState
from form_feedback import detect_symmetry, detect_torso_tilt, calculate_rom

detector = PoseDetector()
rep_counter = RepCounter(min_angle=50.0, max_angle=180.0, threshold_percent=0.25)
angle_filter = MovingAverageFilter(window_size=5)
angles_history = []
session_angles = []
current_symmetry_score = 0.0
current_angle = None

def get_landmark_coords(landmarks, idx):
    if landmarks and idx < len(landmarks):
        lm = landmarks[idx]
        return (lm.x, lm.y, lm.z)
    return None

def calculate_elbow_angle(landmarks):
    if not landmarks:
        return None, None
    left_shoulder = get_landmark_coords(landmarks, 11)
    left_elbow = get_landmark_coords(landmarks, 13)
    left_wrist = get_landmark_coords(landmarks, 15)
    right_shoulder = get_landmark_coords(landmarks, 12)
    right_elbow = get_landmark_coords(landmarks, 14)
    right_wrist = get_landmark_coords(landmarks, 16)
    left_angle = None
    right_angle = None
    if left_shoulder and left_elbow and left_wrist:
        left_angle = calculate_angle_from_points(left_shoulder, left_elbow, left_wrist)
    if right_shoulder and right_elbow and right_wrist:
        right_angle = calculate_angle_from_points(right_shoulder, right_elbow, right_wrist)
    return left_angle, right_angle

def calculate_knee_angle(landmarks):
    if not landmarks:
        return None, None
    left_hip = get_landmark_coords(landmarks, 23)
    left_knee = get_landmark_coords(landmarks, 25)
    left_ankle = get_landmark_coords(landmarks, 27)
    right_hip = get_landmark_coords(landmarks, 24)
    right_knee = get_landmark_coords(landmarks, 26)
    right_ankle = get_landmark_coords(landmarks, 28)
    left_angle = None
    right_angle = None
    if left_hip and left_knee and left_ankle:
        left_angle = calculate_angle_from_points(left_hip, left_knee, left_ankle)
    if right_hip and right_knee and right_ankle:
        right_angle = calculate_angle_from_points(right_hip, right_knee, right_ankle)
    return left_angle, right_angle

def get_current_metrics():
    global current_symmetry_score, current_angle
    rom = 0.0
    if len(angles_history) >= 2:
        rom_val = calculate_rom(angles_history[-30:])
        rom = rom_val if rom_val else 0.0
    return {
        'rep_count': rep_counter.get_count(),
        'state': rep_counter.get_state().value,
        'current_angle': current_angle,
        'symmetry_score': current_symmetry_score,
        'torso_tilt': 0.0,
        'rom': rom
    }

def generate_frames():
    global angles_history, session_angles, current_symmetry_score, current_angle
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not access webcam.")
    while True:
        success, frame = cap.read()
        if not success:
            break
        results = detector.process(frame)
        if results and results.pose_landmarks:
            landmarks = results.pose_landmarks[0]
            left_knee, right_knee = calculate_knee_angle(landmarks)
            left_elbow, right_elbow = calculate_elbow_angle(landmarks)
            angle = None
            sym_score = 0.0
            
            if left_knee and right_knee:
                angle = (left_knee + right_knee) / 2
                is_sym, sym_score = detect_symmetry(left_knee, right_knee)
                current_symmetry_score = sym_score
            elif left_knee:
                angle = left_knee
                sym_score = 50.0
                current_symmetry_score = sym_score
            elif right_knee:
                angle = right_knee
                sym_score = 50.0
                current_symmetry_score = sym_score
            elif left_elbow and right_elbow:
                angle = (left_elbow + right_elbow) / 2
                is_sym, sym_score = detect_symmetry(left_elbow, right_elbow)
                current_symmetry_score = sym_score
            else:
                sym_score = current_symmetry_score
                angle = current_angle
            
            if angle is not None:
                current_angle = angle
                smoothed_angle = angle_filter.update(angle)
                angles_history.append(smoothed_angle)
                session_angles.append(smoothed_angle)
                if len(angles_history) > 100:
                    angles_history.pop(0)
                
                completed_rep = rep_counter.update(smoothed_angle)
                
                left_shoulder = get_landmark_coords(landmarks, 11)
                right_shoulder = get_landmark_coords(landmarks, 12)
                left_hip = get_landmark_coords(landmarks, 23)
                right_hip = get_landmark_coords(landmarks, 24)
                is_tilted, tilt_angle = detect_torso_tilt(
                    left_shoulder, right_shoulder, left_hip, right_hip
                )
                
                state_color = (0, 255, 0) if rep_counter.get_state() != RepState.REP_DONE else (0, 255, 255)
                cv2.putText(frame, f"Reps: {rep_counter.get_count()}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, state_color, 2)
                cv2.putText(frame, f"State: {rep_counter.get_state().value}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, state_color, 2)
                cv2.putText(frame, f"Angle: {smoothed_angle:.1f}°", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                cv2.putText(frame, f"Symmetry: {sym_score:.1f}%", (10, 120),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                if completed_rep:
                    cv2.putText(frame, f"REP {completed_rep}!", (frame.shape[1]//2 - 100, 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
            else:
                current_angle = None
        else:
            current_angle = None
        
        frame = detector.draw_landmarks(frame, results)
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    cap.release()
