import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

class PoseDetector:
    def __init__(self):
        import os
        model_path = os.path.join(os.path.dirname(__file__), "pose_landmarker.task")
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            base_options = python.BaseOptions(
                model_asset_path=model_path,
                delegate=python.BaseOptions.Delegate.CPU
            )
            options = vision.PoseLandmarkerOptions(
                base_options=base_options,
                output_segmentation_masks=False,
                min_pose_detection_confidence=0.6,
                min_pose_presence_confidence=0.6,
                min_tracking_confidence=0.6
            )
            self.detector = vision.PoseLandmarker.create_from_options(options)
            self.use_new_api = True
        except Exception as e:
            print(f"Error initializing MediaPipe: {e}")
            self.use_new_api = False

    def process(self, frame):
        if not self.use_new_api:
            return None
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = self.detector.detect(mp_image)
        return detection_result

    def draw_landmarks(self, frame, detection_result):
        if not detection_result or not detection_result.pose_landmarks:
            return frame
        
        h, w, _ = frame.shape
        for pose_landmarks in detection_result.pose_landmarks:
            points = []
            for landmark in pose_landmarks:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                points.append((x, y))
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            
            connections = [
                (0, 1), (1, 2), (2, 3), (3, 7),
                (0, 4), (4, 5), (5, 6), (6, 8),
                (9, 10), (11, 12), (11, 13), (13, 15),
                (15, 17), (15, 19), (15, 21), (17, 19),
                (12, 14), (14, 16), (16, 18), (16, 20),
                (16, 22), (18, 20), (11, 23), (12, 24),
                (23, 24), (23, 25), (24, 26), (25, 27),
                (26, 28), (27, 29), (27, 31), (28, 30),
                (28, 32), (29, 31), (30, 32)
            ]
            
            for connection in connections:
                if connection[0] < len(points) and connection[1] < len(points):
                    cv2.line(frame, points[connection[0]], points[connection[1]], (0, 255, 0), 2)
        
        return frame
