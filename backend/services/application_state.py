from typing import Optional
from backend.services.database_service import DatabaseManager
from backend.services.roboflow_service import RoboflowManager

class ApplicationState:
    _instance = None
    
    def __init__(self):
        if ApplicationState._instance is not None:
            raise Exception("ApplicationState is a singleton!")
        
        self._db_instance: Optional[DatabaseManager] = None
        self._rf_instance: Optional[RoboflowManager] = None
        self.internet_connected = False
        self.db_connected = False
        self.rf_connected = False
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ApplicationState()
        return cls._instance
    
    @property
    def database(self) -> Optional[DatabaseManager]:
        return self._db_instance
        
    @property
    def roboflow(self) -> Optional[RoboflowManager]:
        return self._rf_instance
    
    def initialize_database(self) -> None:
        if self._db_instance is None:
            self._db_instance = DatabaseManager.get_instance()
            
    def initialize_roboflow(self) -> None:
        if self._rf_instance is None:
            self._rf_instance = RoboflowManager.get_instance()
    
    def update_connection_status(self, internet=None, database=None, roboflow=None):
        if internet is not None:
            self.internet_connected = internet
        if database is not None:
            self.db_connected = database
        if roboflow is not None:
            self.rf_connected = roboflow
