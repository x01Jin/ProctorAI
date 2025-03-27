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
            
    def initialize_roboflow(self) -> bool:
        if self._rf_instance is None:
            self._rf_instance = RoboflowManager.get_instance()
        return self._rf_instance.initialize()

    def reinitialize_roboflow(self) -> bool:
        """Reinitialize Roboflow with new settings."""
        if self._rf_instance:
            self._rf_instance = None  # Clear the instance to force reinitialization
        self.initialize_roboflow()  # This will create a new instance
        if self._rf_instance and self._rf_instance.initialize():
            return True
        return False
    
    def update_connection_status(self, internet=None, database=None, roboflow=None):
        if internet is not None:
            self.internet_connected = internet
        if database is not None:
            self.db_connected = database
        if roboflow is not None:
            self.rf_connected = roboflow
