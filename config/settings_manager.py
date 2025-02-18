from pathlib import Path
import json
import os
from dotenv import load_dotenv

class SettingsManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.settings_file = "app_settings.json"
        self.env = os.getenv('APP_ENV', 'development')
        
        load_dotenv()
        
        self._default_settings = {
            "theme": "dark",
            "roboflow": {
                "api_key": os.getenv('ROBOFLOW_API_KEY', ''),
                "project": os.getenv('ROBOFLOW_PROJECT', ''),
                "model_version": int(os.getenv('ROBOFLOW_MODEL_VERSION', '1'))
            },
            "database": {
                "host": os.getenv('DB_HOST', 'localhost'),
                "user": os.getenv('DB_USER', 'root'),
                "password": os.getenv('DB_PASSWORD', ''),
                "database": os.getenv('DB_NAME', 'proctorai')
            }
        }
        
        self._settings_data = self.load_settings()
    
    def load_settings(self):
        settings = self._default_settings.copy()
        if Path(self.settings_file).exists():
            with open(self.settings_file, 'r') as f:
                stored_settings = json.load(f)
                settings = self._merge_settings(settings, stored_settings)
        else:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
        return settings
    
    def _merge_settings(self, default, stored):
        result = default.copy()
        for key, value in stored.items():
            if isinstance(value, dict) and key in result:
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self._settings_data, f, indent=4)
    
    def get_setting(self, category, key=None):
        if key:
            return self._settings_data.get(category, {}).get(key)
        return self._settings_data.get(category)
    
    def update_setting(self, category, key, value):
        if key is None:
            self._settings_data[category] = value
        else:
            if category not in self._settings_data:
                self._settings_data[category] = {}
            self._settings_data[category][key] = value
        self.save_settings()
    
    def validate_settings(self):
        if self.has_empty_credentials():
            raise ValueError("Required credentials are missing")

    def has_empty_credentials(self):
        if not self.get_setting("roboflow", "api_key"):
            return True
        
        db_settings = self.get_setting("database")
        required_db_fields = ["host", "user", "database"]
        for field in required_db_fields:
            if not db_settings.get(field):
                return True
                
        return False