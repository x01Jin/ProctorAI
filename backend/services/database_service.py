import mysql.connector
from mysql.connector import Error
from config.database_config import DB_CONFIG

class DatabaseManager:
    last_error = None
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DatabaseManager()
        return cls._instance
    
    def __init__(self):
        if DatabaseManager._instance is not None:
            raise Exception("DatabaseManager is a singleton!")
        self.connection = None
    
    def test_connection(self):
        try:
            self.connect()
            if self.connection and self.connection.is_connected():
                return True
            return False
        except Error:
            return False
        finally:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                return True
        except Error as e:
            DatabaseManager.last_error = str(e)
            self.connection = None
        return False

    def ensure_connection(self):
        if self.connection is None or not self.connection.is_connected():
            self.connect()

    def insert_report_details(self, proctor, block, date, subject, room, start, end, num_students):
        self.ensure_connection()
        if self.connection is None:
            DatabaseManager.last_error = "No database connection"
            return

        try:
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
        except Error as e:
            DatabaseManager.last_error = str(e)


def get_database():
    return DatabaseManager.get_instance()
