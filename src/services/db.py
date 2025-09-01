import json
import os
import uuid
from typing import Dict, Any

class DBService:
    def __init__(self):
        self.db_file = "sessions.json"
        self.db = self._load_db()

    def _load_db(self) -> Dict[str, Any]:
        """Load the database from the JSON file."""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def _save_db(self) -> None:
        """Save the database to the JSON file."""
        with open(self.db_file, 'w') as f:
            json.dump(self.db, f)

    def get_session(self, session_id: str):
        return self.db.get(session_id)
    
    def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid.uuid4())
        self.db[session_id] = {}
        self._save_db()
        return session_id
        
    def save_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """Save a session to the database."""
        self.db[session_id] = data
        self._save_db()
        
    def delete_session(self, session_id: str) -> bool:
        """Delete a session from the database."""
        if session_id in self.db:
            del self.db[session_id]
            self._save_db()
            return True
        return False
