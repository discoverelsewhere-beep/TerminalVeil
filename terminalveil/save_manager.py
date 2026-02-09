"""
Terminal Veil - Save System
"""
import json
import os

class SaveManager:
    def __init__(self, filename='veil_save.json'):
        self.filepath = os.path.join(os.path.expanduser('~'), filename)
        try:
            from android.storage import app_storage_path
            self.filepath = os.path.join(app_storage_path(), filename)
        except ImportError:
            pass
    
    def save(self, state):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(state, f)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def load(self):
        if not os.path.exists(self.filepath):
            return None
        try:
            with open(self.filepath, 'r') as f:
                state = json.load(f)
            if 'current_level' in state and 'inventory' in state:
                return state
        except Exception as e:
            print(f"Load error: {e}")
        return None
