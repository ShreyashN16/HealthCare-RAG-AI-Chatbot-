import numpy as np
from typing import List, Optional, Tuple
from collections import deque
from datetime import datetime, timedelta


def detect_symmetry(left_angle: float, right_angle: float, tolerance: float = 10.0) -> Tuple[bool, float]:
    """
    Detect symmetry between left and right side angles.
    
    Args:
        left_angle: Angle from left side
        right_angle: Angle from right side
        tolerance: Maximum difference for symmetric movement
        
    Returns:
        Tuple of (is_symmetric, symmetry_score) where score is 0-100
    """
    if left_angle is None or right_angle is None:
        return False, 0.0
    
    diff = abs(left_angle - right_angle)
    is_symmetric = diff <= tolerance
    
    score = max(0.0, 100.0 - (diff / tolerance * 100.0))
    score = min(100.0, score)
    
    return is_symmetric, score


def detect_torso_tilt(shoulder_left: Tuple[float, float, float],
                      shoulder_right: Tuple[float, float, float],
                      hip_left: Tuple[float, float, float],
                      hip_right: Tuple[float, float, float]) -> Tuple[bool, float]:
    """
    Detect torso tilt by comparing shoulder and hip alignment.
    
    Args:
        shoulder_left: Left shoulder coordinates (x, y, z)
        shoulder_right: Right shoulder coordinates (x, y, z)
        hip_left: Left hip coordinates (x, y, z)
        hip_right: Right hip coordinates (x, y, z)
        
    Returns:
        Tuple of (is_tilted, tilt_angle) in degrees
    """
    if None in [shoulder_left, shoulder_right, hip_left, hip_right]:
        return True, 0.0
    
    shoulder_center_x = (shoulder_left[0] + shoulder_right[0]) / 2
    hip_center_x = (hip_left[0] + hip_right[0]) / 2
    
    shoulder_center_y = (shoulder_left[1] + shoulder_right[1]) / 2
    hip_center_y = (hip_left[1] + hip_right[1]) / 2
    
    dx = hip_center_x - shoulder_center_x
    dy = hip_center_y - shoulder_center_y
    
    tilt_angle = np.degrees(np.arctan2(abs(dx), abs(dy)))
    
    is_tilted = tilt_angle > 5.0
    
    return is_tilted, tilt_angle


def calculate_rom(angles: List[float]) -> Optional[float]:
    """
    Calculate range of motion from a list of angles.
    
    Args:
        angles: List of angle values over time
        
    Returns:
        Range of motion (max - min) or None if insufficient data
    """
    if not angles or len(angles) < 2:
        return None
    
    valid_angles = [a for a in angles if a is not None]
    if len(valid_angles) < 2:
        return None
    
    return max(valid_angles) - min(valid_angles)


class TempoCalculator:
    """Calculate tempo (speed) of ascending and descending phases."""
    
    def __init__(self):
        self.phase_start_angle: Optional[float] = None
        self.phase_start_time: Optional[datetime] = None
        self.current_phase: Optional[str] = None  # 'ascending' or 'descending'
        self.last_angle: Optional[float] = None
    
    def update(self, angle: float) -> Tuple[Optional[float], Optional[float]]:
        """
        Update with new angle and return tempo values.
        
        Args:
            angle: Current angle value
            
        Returns:
            Tuple of (tempo_up, tempo_down) in seconds per degree, or (None, None)
        """
        if self.last_angle is None:
            self.last_angle = angle
            return None, None
        
        now = datetime.now()
        tempo_up = None
        tempo_down = None
        
        if self.last_angle is not None and angle is not None:
            if angle > self.last_angle:
                if self.current_phase != 'ascending':
                    self.current_phase = 'ascending'
                    self.phase_start_angle = self.last_angle
                    self.phase_start_time = now
            elif angle < self.last_angle:
                if self.current_phase != 'descending':
                    if self.current_phase == 'ascending' and self.phase_start_time:
                        duration = (now - self.phase_start_time).total_seconds()
                        angle_diff = abs(angle - self.phase_start_angle)
                        if angle_diff > 0:
                            tempo_up = duration / angle_diff
                    
                    self.current_phase = 'descending'
                    self.phase_start_angle = self.last_angle
                    self.phase_start_time = now
                elif self.current_phase == 'descending' and self.phase_start_time:
                    duration = (now - self.phase_start_time).total_seconds()
                    angle_diff = abs(self.phase_start_angle - angle)
                    if angle_diff > 5.0:
                        tempo_down = duration / angle_diff
                        self.phase_start_time = None
        
        self.last_angle = angle
        return tempo_up, tempo_down
    
    def reset(self):
        """Reset calculator state."""
        self.phase_start_angle = None
        self.phase_start_time = None
        self.current_phase = None
        self.last_angle = None
