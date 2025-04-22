from roboflow import Roboflow
from config import settings_manager
import sys
import logging
from backend.utils.log_config import _logger_stream_handler

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    cls.get_instance = staticmethod(get_instance)
    return cls

class SplashLogWriter:
    def __init__(self, splash_screen):
        self.splash_screen = splash_screen
        self.original_stdout = sys.stdout
        self.logger = logging.getLogger('roboflow')

    def write(self, text):
        if text.strip():
            self.splash_screen.log(text.strip())
            self.logger.debug(text.strip())

    def flush(self):
        if self.original_stdout:
            self.original_stdout.flush()

@singleton
class RoboflowManager:
    last_error = None

    def __init__(self):
        self._model = None
        self._classes = []
        self.logger = logging.getLogger('roboflow')
        self.logger.setLevel(logging.INFO)

    @property
    def model(self):
        return self._model

    @property
    def classes(self):
        return self._classes

    def initialize(self, splash_screen=None):
        original_stdout = sys.stdout
        fallback_logger = None
        try:
            if splash_screen:
                sys.stdout = SplashLogWriter(splash_screen)
            elif sys.stdout is None:
                fallback_logger = _logger_stream_handler(logging.getLogger('roboflow'))
                sys.stdout = fallback_logger
            api_key = settings_manager.get_setting("roboflow", "api_key")
            project_name = settings_manager.get_setting("roboflow", "project")
            model_version = settings_manager.get_setting("roboflow", "model_version")
            self.logger.info(f"Connecting to Roboflow (Project: {project_name}, Version: {model_version})")
            rf = Roboflow(api_key=api_key)
            project = rf.workspace().project(project_name)
            self._model = project.version(model_version).model
            model_classes = settings_manager.get_setting("roboflow", "model_classes")
            if not model_classes:
                raise ValueError("No model classes specified in settings")
            self._classes = [cls.strip() for cls in model_classes.split(",") if cls.strip()]
            if not self._classes:
                raise ValueError("No valid classes found after parsing model_classes setting")
            self.logger.info(f"Model initialized with classes: {', '.join(self._classes)}")
            return True
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Failed to initialize Roboflow: {error_msg}")
            RoboflowManager.last_error = error_msg
            return False
        finally:
            if splash_screen or fallback_logger:
                sys.stdout = original_stdout

def get_roboflow():
    return RoboflowManager.get_instance()
