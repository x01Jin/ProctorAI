from roboflow import Roboflow
from config.settings_manager import SettingsManager
import sys

class SplashLogWriter:
    def __init__(self, splash_screen):
        self.splash_screen = splash_screen
        self.original_stdout = sys.stdout

    def write(self, text):
        if text.strip():  # Only log non-empty lines
            self.splash_screen.log_message(text.strip())
        if self.original_stdout:
            self.original_stdout.write(text)

    def flush(self):
        if self.original_stdout:
            self.original_stdout.flush()

class RoboflowManager:
    _instance = None
    last_error = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = RoboflowManager()
        return cls._instance
    
    def __init__(self):
        if RoboflowManager._instance is not None:
            raise Exception("RoboflowManager is a singleton!")
        self._model = None
        self._classes = ["cheating", "not_cheating"]
    
    @property
    def model(self):
        return self._model
        
    @property
    def classes(self):
        return self._classes
    
    def initialize(self, splash_screen=None):
        settings = SettingsManager()
        original_stdout = sys.stdout
        try:
            if splash_screen:
                sys.stdout = SplashLogWriter(splash_screen)
            
            rf = Roboflow(api_key=settings.get_setting("roboflow", "api_key"))
            project = rf.workspace().project(settings.get_setting("roboflow", "project"))
            self._model = project.version(settings.get_setting("roboflow", "model_version")).model
            return True
        except Exception as e:
            RoboflowManager.last_error = str(e)
            return False
        finally:
            if splash_screen:
                sys.stdout = original_stdout

def get_roboflow():
    return RoboflowManager.get_instance()
