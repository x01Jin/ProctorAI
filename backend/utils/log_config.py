import logging
from logging.handlers import RotatingFileHandler
import os
import sys

def setup_logging():
    try:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        log_dir = os.path.join(base_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
    
        log_format = '%(asctime)s - %(name)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s'
        
        # Configure main application logger
        main_handler = RotatingFileHandler(
            os.path.join(log_dir, "proctorai.log"),
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        main_handler.setFormatter(logging.Formatter(log_format))
        
        # Configure component-specific loggers
        components = ['camera', 'detection', 'report', 'database', 'roboflow']
        for component in components:
            handler = RotatingFileHandler(
                os.path.join(log_dir, f"{component}.log"),
                maxBytes=5*1024*1024,
                backupCount=3
            )
            handler.setFormatter(logging.Formatter(log_format))
            component_logger = logging.getLogger(component)
            if component == 'database':
                component_logger.setLevel(logging.INFO)
            elif component in ['roboflow', 'detection', 'camera']:
                component_logger.setLevel(logging.DEBUG)
            else:
                component_logger.setLevel(logging.ERROR)
            component_logger.addHandler(handler)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.ERROR)
        root_logger.addHandler(main_handler)
        
        # Add console output in development mode
        if not getattr(sys, 'frozen', False):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(log_format))
            root_logger.addHandler(console_handler)

        # Only redirect stdout/stderr if we have a console
        if sys.stdout is not None and sys.stderr is not None:
            sys.stdout = LoggerStreamHandler(logging.getLogger('stdout'))
            sys.stderr = LoggerStreamHandler(logging.getLogger('stderr'))
    except Exception as e:
        if not getattr(sys, 'frozen', False):
            print(f"Error setting up logging: {str(e)}")

class LoggerStreamHandler:
    def __init__(self, logger):
        self.logger = logger

    def write(self, message):
        if message and not message.isspace():
            self.logger.info(message.strip())

    def flush(self):
        pass
