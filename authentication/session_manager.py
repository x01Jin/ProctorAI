import os
import json

SESSION_FILE = "session.json"

class SessionManager:
    def __init__(self, session_file=SESSION_FILE):
        self.session_file = session_file

    def save_session(self, user_id):
        session_data = {
            "user_id": user_id
        }
        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f)

    def load_session(self):
        if not os.path.exists(self.session_file):
            return None
        with open(self.session_file, "r", encoding="utf-8") as f:
            session_data = json.load(f)
        return session_data.get("user_id")

    def clear_session(self):
        if os.path.exists(self.session_file):
            os.remove(self.session_file)