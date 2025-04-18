from typing import Optional
from backend.services.database_service import DatabaseManager
from backend.services.roboflow_service import RoboflowManager

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    cls.get_instance = staticmethod(get_instance)
    return cls

@singleton
class ApplicationState:
    def __init__(self):
        self._db_instance: Optional[DatabaseManager] = None
        self._rf_instance: Optional[RoboflowManager] = None
        self.db_connected = False
        self.rf_connected = False

    @property
    def database(self) -> Optional[DatabaseManager]:
        return self._db_instance

    @property
    def roboflow(self) -> Optional[RoboflowManager]:
        return self._rf_instance

    def initialize_database(self) -> None:
        if self._db_instance is None:
            self._db_instance = DatabaseManager.get_instance()

    def initialize_roboflow(self) -> bool:
        if self._rf_instance is None:
            self._rf_instance = RoboflowManager.get_instance()
        return True

    def reinitialize_roboflow(self) -> bool:
        self._rf_instance = None
        self.initialize_roboflow()
        if self._rf_instance and self._rf_instance.initialize():
            return True
        return False

    def update_connection_status(self, database=None, roboflow=None):
        if database is not None:
            self.db_connected = database
        if roboflow is not None:
            self.rf_connected = roboflow
