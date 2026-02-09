import numpy as np
from typing import List, Tuple, Optional
from collections import deque


def calculate_vector(point1: Tuple[float, float, float], 
                     point2: Tuple[float, float, float]) -> np.ndarray:
    """
    Calculate vector from point1 to point2.
    
    Args:
        point1: (x, y, z) coordinates
        point2: (x, y, z) coordinates
        
    Returns:
        3D vector as numpy array
    """
    return np.array(point2) - np.array(point1)


def calculate_angle(vector1: np.ndarray, vector2: np.ndarray) -> float:
    """
    Calculate angle between two vectors using dot product.
    
    Args:
        vector1: First vector
        vector2: Second vector
        
    Returns:
        Angle in degrees
    """
    dot_product = np.dot(vector1, vector2)
    magnitude1 = np.linalg.norm(vector1)
    magnitude2 = np.linalg.norm(vector2)
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    cos_angle = np.clip(dot_product / (magnitude1 * magnitude2), -1.0, 1.0)
    angle_rad = np.arccos(cos_angle)
    angle_deg = np.degrees(angle_rad)
    
    return angle_deg


def calculate_angle_from_points(point1: Tuple[float, float, float],
                                point2: Tuple[float, float, float],
                                point3: Tuple[float, float, float]) -> float:
    """
    Calculate angle at point2 formed by point1-point2-point3.
    
    Args:
        point1: First point
        point2: Vertex point
        point3: Third point
        
    Returns:
        Angle in degrees
    """
    vec1 = calculate_vector(point2, point1)
    vec2 = calculate_vector(point2, point3)
    return calculate_angle(vec1, vec2)


class MovingAverageFilter:
    """Moving average filter for smoothing angle values."""
    
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.values = deque(maxlen=window_size)
    
    def update(self, value: float) -> float:
        """
        Add new value and return smoothed average.
        
        Args:
            value: New angle value
            
        Returns:
            Smoothed average value
        """
        self.values.append(value)
        return np.mean(self.values)
    
    def reset(self):
        """Clear all stored values."""
        self.values.clear()
    
    def get_current(self) -> Optional[float]:
        """Get current smoothed value without updating."""
        if len(self.values) == 0:
            return None
        return np.mean(self.values)
