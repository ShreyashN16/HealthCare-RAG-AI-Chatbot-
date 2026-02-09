from enum import Enum
from typing import Optional
import numpy as np


class RepState(Enum):
    REST = "REST"
    DOWN = "DOWN"
    UP = "UP"
    REP_DONE = "REP_DONE"


class RepCounter:
    def __init__(self,
                 min_angle: float = 60.0,
                 max_angle: float = 170.0,
                 threshold_percent: float = 0.3):
        """
        Improved state machine for counting exercise reps using adaptive thresholds.
        
        Args:
            min_angle: Minimum angle observed (will be auto-calibrated)
            max_angle: Maximum angle observed (will be auto-calibrated)
            threshold_percent: Percentage of range for state transitions (0.3 = 30%)
        """
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.threshold_percent = threshold_percent
        self.auto_calibrate = True
        self.calibration_samples = []
        
        self.state = RepState.REST
        self.rep_count = 0
        self.last_angle: Optional[float] = None
        self.peak_angle = 0.0
        self.valley_angle = 180.0
    
    def _update_calibration(self, angle: float):
        """Update min/max angles for auto-calibration."""
        if self.auto_calibrate:
            self.calibration_samples.append(angle)
            if len(self.calibration_samples) > 50:
                self.calibration_samples.pop(0)
            
            if len(self.calibration_samples) >= 10:
                self.min_angle = min(self.calibration_samples[-30:])
                self.max_angle = max(self.calibration_samples[-30:])
                
                if self.max_angle - self.min_angle < 20:
                    self.min_angle = max(40.0, self.min_angle - 20)
                    self.max_angle = min(180.0, self.max_angle + 20)
    
    def _get_thresholds(self):
        """Calculate dynamic thresholds based on observed range."""
        angle_range = self.max_angle - self.min_angle
        down_threshold = self.min_angle + (angle_range * self.threshold_percent)
        up_threshold = self.max_angle - (angle_range * self.threshold_percent)
        return down_threshold, up_threshold
    
    def update(self, angle: float) -> Optional[int]:
        """
        Update state machine with new angle value.
        
        Args:
            angle: Current angle value
            
        Returns:
            Rep count if rep completed, None otherwise
        """
        if angle is None:
            return None
        
        self._update_calibration(angle)
        self.last_angle = angle
        
        completed_rep = None
        down_threshold, up_threshold = self._get_thresholds()
        
        if self.state == RepState.REST:
            if angle <= down_threshold:
                self.state = RepState.DOWN
                self.valley_angle = angle
        
        elif self.state == RepState.DOWN:
            if angle < self.valley_angle:
                self.valley_angle = angle
            if angle >= up_threshold:
                self.state = RepState.UP
                self.peak_angle = angle
        
        elif self.state == RepState.UP:
            if angle > self.peak_angle:
                self.peak_angle = angle
            if angle <= down_threshold:
                self.state = RepState.REP_DONE
                self.rep_count += 1
                completed_rep = self.rep_count
                self.state = RepState.DOWN
                self.valley_angle = angle
        
        elif self.state == RepState.REP_DONE:
            if angle <= down_threshold:
                self.state = RepState.DOWN
        
        return completed_rep
    
    def get_count(self) -> int:
        """Get current rep count."""
        return self.rep_count
    
    def get_state(self) -> RepState:
        """Get current state."""
        return self.state
    
    def reset(self):
        """Reset counter and state."""
        self.state = RepState.REST
        self.rep_count = 0
        self.last_angle = None
        self.peak_angle = 0.0
        self.valley_angle = 180.0
        self.calibration_samples = []