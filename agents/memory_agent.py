"""
Memory Agent for Farm History Tracking
Maintains user session data, crop history, and follow-up schedules
"""
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from config import Config


class MemoryAgent:
    """
    Agent responsible for persistent state management.
    
    This agent:
    1. Stores user farm history in SQLite database
    2. Tracks disease occurrences per crop
    3. Maintains follow-up schedules
    4. Provides historical context for better diagnosis
    5. Manages user sessions
    
    Note: This is not a Workflow Executor, but a utility service
    used by other agents to persist and retrieve data.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize Memory Agent with database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            db_path = Config.DATA_DIR / "farm_memory.db"
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema if not exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                location TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Farm sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farm_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                image_path TEXT,
                plant_type TEXT,
                disease_detected TEXT,
                confidence REAL,
                diagnosis_json TEXT,
                action_plan TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Follow-ups table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS follow_ups (
                follow_up_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                user_id TEXT,
                scheduled_date DATE,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                completed_at TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES farm_sessions(session_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Disease history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS disease_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                plant_type TEXT,
                disease_name TEXT,
                occurrence_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                treatment_applied TEXT,
                outcome TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_user(self, user_id: str, name: str, location: str, phone: str = "") -> bool:
        """
        Create a new user profile.
        
        Args:
            user_id: Unique user identifier
            name: User's name
            location: Farm location
            phone: Contact number
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO users (user_id, name, location, phone) VALUES (?, ?, ?, ?)",
                (user_id, name, location, phone)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def register_user(self, user_id: str, name: str, location: str, phone: str = "") -> bool:
        """
        Register a new user profile (alias for create_user).
        
        Args:
            user_id: Unique user identifier
            name: User's name
            location: Farm location
            phone: Contact number
            
        Returns:
            True if successful
        """
        return self.create_user(user_id, name, location, phone)
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information.
        
        Args:
            user_id: User identifier
            
        Returns:
            User info dictionary or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, name, location, phone, created_at FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "user_id": row[0],
                    "name": row[1],
                    "location": row[2],
                    "phone": row[3],
                    "created_at": row[4]
                }
            return None
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def save_session(
        self,
        user_id: str,
        image_path: str,
        plant_type: str,
        disease_detected: str,
        confidence: float,
        diagnosis_json: str,
        action_plan: str
    ) -> Optional[int]:
        """
        Save a diagnosis session.
        
        Args:
            user_id: User identifier
            image_path: Path to uploaded image
            plant_type: Type of crop/plant
            disease_detected: Disease name
            confidence: Confidence score
            diagnosis_json: Full diagnosis JSON
            action_plan: Generated action plan
            
        Returns:
            Session ID if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO farm_sessions 
                (user_id, image_path, plant_type, disease_detected, confidence, diagnosis_json, action_plan)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, image_path, plant_type, disease_detected, confidence, diagnosis_json, action_plan))
            
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return session_id
        except Exception as e:
            print(f"Error saving session: {e}")
            return None
    
    def schedule_follow_up(self, session_id: int, user_id: str, days_ahead: int = 2, notes: str = "") -> bool:
        """
        Schedule a follow-up for a session.
        
        Args:
            session_id: Session to follow up on
            user_id: User identifier
            days_ahead: Days from now to schedule
            notes: Additional notes
            
        Returns:
            True if successful
        """
        try:
            follow_up_date = datetime.now() + timedelta(days=days_ahead)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO follow_ups (session_id, user_id, scheduled_date, notes)
                VALUES (?, ?, ?, ?)
            """, (session_id, user_id, follow_up_date.date(), notes))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error scheduling follow-up: {e}")
            return False
    
    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get user's diagnosis history.
        
        Args:
            user_id: User identifier
            limit: Maximum number of records
            
        Returns:
            List of session dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, plant_type, disease_detected, confidence, created_at
                FROM farm_sessions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    "session_id": row[0],
                    "plant_type": row[1],
                    "disease_detected": row[2],
                    "confidence": row[3],
                    "date": row[4]
                })
            
            return history
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []
    
    def get_pending_follow_ups(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get pending follow-ups for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of pending follow-ups
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT f.follow_up_id, f.session_id, f.scheduled_date, f.notes, s.disease_detected
                FROM follow_ups f
                JOIN farm_sessions s ON f.session_id = s.session_id
                WHERE f.user_id = ? AND f.status = 'pending'
                ORDER BY f.scheduled_date ASC
            """, (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            follow_ups = []
            for row in rows:
                follow_ups.append({
                    "follow_up_id": row[0],
                    "session_id": row[1],
                    "scheduled_date": row[2],
                    "notes": row[3],
                    "disease": row[4]
                })
            
            return follow_ups
        except Exception as e:
            print(f"Error fetching follow-ups: {e}")
            return []
    
    def mark_follow_up_complete(self, follow_up_id: int, notes: str = "") -> bool:
        """
        Mark a follow-up as completed.
        
        Args:
            follow_up_id: Follow-up identifier
            notes: Completion notes
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE follow_ups
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP, notes = ?
                WHERE follow_up_id = ?
            """, (notes, follow_up_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking follow-up complete: {e}")
            return False
    
    def get_disease_patterns(self, user_id: str, plant_type: str) -> Dict[str, Any]:
        """
        Analyze disease patterns for a user's specific crop.
        
        Args:
            user_id: User identifier
            plant_type: Crop type to analyze
            
        Returns:
            Pattern analysis dictionary
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT disease_detected, COUNT(*) as count, AVG(confidence) as avg_confidence
                FROM farm_sessions
                WHERE user_id = ? AND plant_type = ?
                GROUP BY disease_detected
                ORDER BY count DESC
            """, (user_id, plant_type))
            
            rows = cursor.fetchall()
            conn.close()
            
            patterns = {
                "most_common_diseases": [
                    {"disease": row[0], "occurrences": row[1], "avg_confidence": row[2]}
                    for row in rows
                ],
                "total_diagnoses": sum(row[1] for row in rows)
            }
            
            return patterns
        except Exception as e:
            print(f"Error analyzing patterns: {e}")
            return {"error": str(e)}
