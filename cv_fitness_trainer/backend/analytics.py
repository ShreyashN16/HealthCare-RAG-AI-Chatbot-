from tinydb import TinyDB, Query
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel


class SessionMetrics(BaseModel):
    timestamp: str
    exercise: str
    valid_reps: int
    symmetry_score: float
    rom: Optional[float]
    tempo_up: Optional[float]
    tempo_down: Optional[float]


class AnalyticsDB:
    def __init__(self, db_path: str = "analytics.json"):
        """
        Initialize TinyDB for storing session analytics.
        
        Args:
            db_path: Path to the JSON database file
        """
        self.db = TinyDB(db_path)
    
    def save_session(self, 
                    exercise: str,
                    valid_reps: int,
                    symmetry_score: float,
                    rom: Optional[float] = None,
                    tempo_up: Optional[float] = None,
                    tempo_down: Optional[float] = None) -> int:
        """
        Save a training session to the database.
        
        Args:
            exercise: Name of the exercise
            valid_reps: Number of valid reps completed
            symmetry_score: Symmetry score (0-100)
            rom: Range of motion
            tempo_up: Tempo for ascending phase
            tempo_down: Tempo for descending phase
            
        Returns:
            Document ID of the saved session
        """
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "exercise": exercise,
            "valid_reps": valid_reps,
            "symmetry_score": symmetry_score,
            "rom": rom,
            "tempo_up": tempo_up,
            "tempo_down": tempo_down
        }
        
        doc_id = self.db.insert(session_data)
        return doc_id
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all stored sessions."""
        return self.db.all()
    
    def get_sessions_by_exercise(self, exercise: str) -> List[Dict]:
        """
        Get all sessions for a specific exercise.
        
        Args:
            exercise: Exercise name to filter by
            
        Returns:
            List of session documents
        """
        Session = Query()
        return self.db.search(Session.exercise == exercise)
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session documents, sorted by timestamp descending
        """
        all_sessions = self.db.all()
        sorted_sessions = sorted(
            all_sessions,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )
        return sorted_sessions[:limit]
    
    def clear_all(self):
        """Clear all session data."""
        self.db.truncate()
