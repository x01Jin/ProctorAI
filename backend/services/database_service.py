import mysql.connector
from mysql.connector import Error
import logging
from config.database_config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                logging.info("Connection to MySQL database successful")
        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
            self.connection = None

    def ensure_connection(self):
        if self.connection is None or not self.connection.is_connected():
            self.connect()

    def insert_report_details(self, proctor, block, date, subject, room, start, end, num_students):
        self.ensure_connection()
        if self.connection is None:
            logging.error("Failed to insert report details: No database connection")
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
            logging.info("Report details inserted successfully")
        except Error as e:
            logging.error(f"Error inserting report details: {e}")

logging.basicConfig(level=logging.INFO)

db_manager = DatabaseManager()
