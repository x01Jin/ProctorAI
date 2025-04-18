import mysql.connector
from mysql.connector import Error
import logging
from config.settings_manager import SettingsManager

DB_REQUIRED_FIELDS = ['host', 'user', 'database']
DB_LOGGER = logging.getLogger('database')

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    cls.get_instance = staticmethod(get_instance)
    return cls

@singleton
class DatabaseManager:
    last_error = None

    def __init__(self):
        self.connection = None
        self.settings = SettingsManager()

    def get_db_config(self):
        db_settings = self.settings.get_setting('database')
        if not db_settings:
            DatabaseManager.last_error = "Database settings not found"
            DB_LOGGER.error("Database settings not found")
            return None
        for field in DB_REQUIRED_FIELDS:
            if not db_settings.get(field):
                error_msg = f"Missing required database setting: {field}"
                DatabaseManager.last_error = error_msg
                DB_LOGGER.error(error_msg)
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
            DB_LOGGER.error(f"Connection test failed: {error_msg}")
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
                DB_LOGGER.info(f"Successfully connected to MySQL database (Server: {db_info}, Session ID: {session_id})")
                return True
        except Error as e:
            error_msg = str(e)
            DatabaseManager.last_error = error_msg
            DB_LOGGER.error(f"Error connecting to MySQL: {error_msg}")
            self.connection = None
        return False

    def ensure_connection(self):
        if self.connection is None or not self.connection.is_connected():
            DB_LOGGER.info("Attempting to reconnect...")
            self.connect()

    def insert_report_details(self, proctor, block, date, subject, room, start, end, num_students):
        self.ensure_connection()
        if self.connection is None:
            error_msg = "No database connection"
            DatabaseManager.last_error = error_msg
            DB_LOGGER.error(f"Failed to insert report details: {error_msg}")
            return
        try:
            session_id = self.connection.connection_id
            DB_LOGGER.info(f"Beginning report details insert (Session ID: {session_id})")
            with self.connection.cursor() as cursor:
                query = (
                    "INSERT INTO reportlog (proctor, num_students, block, subject, room, start, end, date) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                )
                try:
                    num_students_int = int(num_students)
                except ValueError:
                    raise ValueError("Number of students must be a valid integer")
                values = (proctor, num_students_int, block, subject, room, start, end, date)
                cursor.execute(query, values)
                self.connection.commit()
                DB_LOGGER.info(f"Report details inserted successfully (Session ID: {session_id})")
        except Error as e:
            error_msg = str(e)
            DatabaseManager.last_error = error_msg
            DB_LOGGER.error(f"Error inserting report details (Session ID: {session_id if self.connection else 'None'}): {error_msg}")

def get_database():
    return DatabaseManager.get_instance()
