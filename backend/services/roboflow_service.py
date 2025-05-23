import logging
import sys
from roboflow import Roboflow
from backend.utils.log_config import _logger_stream_handler
from backend.services import database_service

LOGGER = logging.getLogger("roboflow")

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
        self.logger = LOGGER

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
        self.logger = LOGGER
        self.logger.setLevel(logging.INFO)

    @property
    def model(self):
        return self._model

    @property
    def classes(self):
        return self._classes

    def _handle_error(self, error_msg):
        self.logger.error(error_msg)
        RoboflowManager.last_error = error_msg
        return False

    def _set_stdout(self, splash_screen):
        if splash_screen:
            return SplashLogWriter(splash_screen)
        if sys.stdout is None:
            return _logger_stream_handler(LOGGER)
        return None

    def _restore_stdout(self, original_stdout, custom_stdout):
        if custom_stdout:
            sys.stdout = original_stdout

    def _initialize_model(self, roboflow_settings):
        if not roboflow_settings:
            return self._handle_error("No Roboflow settings found in database")

        try:
            api_key = roboflow_settings["api_key"]
            project_name = roboflow_settings["project"]
            model_version = roboflow_settings["model_version"]
            model_classes = roboflow_settings["model_classes"]
        except KeyError as e:
            return self._handle_error(f"Missing required Roboflow setting: {str(e)}")

        if not model_classes:
            return self._handle_error("No model classes specified")

        self.logger.info(f"Connecting to Roboflow (Project: {project_name}, Version: {model_version})")
        try:
            rf = Roboflow(api_key=api_key)
            project = rf.workspace().project(project_name)
            self._model = project.version(model_version).model
            self._classes = [cls.strip() for cls in model_classes.split(",") if cls.strip()]

            if not self._classes:
                return self._handle_error("No valid classes found after parsing model_classes")

            self.logger.info(f"Model initialized with classes: {', '.join(self._classes)}")
            return True
        except Exception as e:
            return self._handle_error(f"Failed to initialize Roboflow: {str(e)}")

    def initialize(self, splash_screen=None):
        original_stdout = sys.stdout
        custom_stdout = self._set_stdout(splash_screen)
        sys.stdout = custom_stdout if custom_stdout else original_stdout

        try:
            roboflow_settings = database_service.fetch_roboflow_settings()
            return self._initialize_model(roboflow_settings)
        finally:
            self._restore_stdout(original_stdout, custom_stdout)

def get_roboflow():
    return RoboflowManager.get_instance()
