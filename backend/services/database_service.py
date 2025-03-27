import mysql.connector
from mysql.connector import Error
import logging
from config.settings_manager import SettingsManager

class DatabaseManager:
    last_error = None
    _instance = None
    logger = logging.getLogger('database')
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DatabaseManager()
        return cls._instance
    
    def __init__(self):
        if DatabaseManager._instance is not None:
            raise Exception("DatabaseManager is a singleton!")
        self.connection = None
        self.settings = SettingsManager()
    
    def get_db_config(self):
        db_settings = self.settings.get_setting('database')
        if not db_settings:
            DatabaseManager.last_error = "Database settings not found"
            self.logger.error("Database settings not found")
            return None
            
        required_fields = ['host', 'user', 'database']
        for field in required_fields:
            if not db_settings.get(field):
                error_msg = f"Missing required database setting: {field}"
                DatabaseManager.last_error = error_msg
                self.logger.error(error_msg)
                return None
                
        return {
            'host': db_settings['host'],
            'user': db_settings['user'],
            'password': db_settings.get('password', ''),
            'database': db_settings['database']
        }
    
    def test_connection(self):
        try:
            self.connect()
            if self.connection and self.connection.is_connected():
                return True
            return False
        except Error as e:
            error_msg = str(e)
            DatabaseManager.last_error = error_msg
            self.logger.error(f"Connection test failed: {error_msg}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                self.connection = None
    
    def connect(self):
        try:
            db_config = self.get_db_config()
            if not db_config:
                return False
                
            self.connection = mysql.connector.connect(**db_config)
            if self.connection.is_connected():
                db_info = self.connection.get_server_info()
                session_id = self.connection.connection_id
                self.logger.info(f"Successfully connected to MySQL database (Server: {db_info}, Session ID: {session_id})")
                return True
        except Error as e:
            error_msg = str(e)
            DatabaseManager.last_error = error_msg
            self.logger.error(f"Error connecting to MySQL: {error_msg}")
            self.connection = None
        return False

    def ensure_connection(self):
        if self.connection is None or not self.connection.is_connected():
            self.logger.info("Attempting to reconnect...")
            self.connect()

    def insert_report_details(self, proctor, block, date, subject, room, start, end, num_students):
        self.ensure_connection()
        if self.connection is None:
            error_msg = "No database connection"
            DatabaseManager.last_error = error_msg
            self.logger.error(f"Failed to insert report details: {error_msg}")
            return

        try:
            session_id = self.connection.connection_id
            self.logger.info(f"Beginning report details insert (Session ID: {session_id})")
            cursor = self.connection.cursor()
            query = """
            INSERT INTO reportlog (proctor, num_students, block, subject, room, start, end, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            try:
                num_students_int = int(num_students)
            except ValueError:
                raise ValueError("Number of students must be a valid integer")
            values = (proctor, num_students_int, block, subject, room, start, end, date)
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            self.logger.info(f"Report details inserted successfully (Session ID: {session_id}, Last Row ID: {cursor.lastrowid})")
        except Error as e:
            error_msg = str(e)
            DatabaseManager.last_error = error_msg
            self.logger.error(f"Error inserting report details (Session ID: {session_id if self.connection else 'None'}): {error_msg}")

def get_database():
    return DatabaseManager.get_instance()
