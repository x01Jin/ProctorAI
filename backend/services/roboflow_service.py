from roboflow import Roboflow
from config.settings_manager import SettingsManager

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
    
    def initialize(self):
        settings = SettingsManager()
        try:
            rf = Roboflow(api_key=settings.get_setting("roboflow", "api_key"))
            project = rf.workspace().project(settings.get_setting("roboflow", "project"))
            self._model = project.version(settings.get_setting("roboflow", "model_version")).model
            return True
        except Exception as e:
            RoboflowManager.last_error = str(e)
            return False

def get_roboflow():
    return RoboflowManager.get_instance()
