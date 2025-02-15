import mysql.connector
from mysql.connector import Error
import os
import logging

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'proctorai')
            )
            if self.connection.is_connected():
                logging.info("Connection to MySQL database successful")
        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
            self.connection = None

    def ensure_connection(self):
        if self.connection is None or not self.connection.is_connected():
            self.connect()

    def insert_report_details(self, proctor, block, date, subject, room, start, end):
        self.ensure_connection()
        if self.connection is None:
            logging.error("Failed to insert report details: No database connection")
            return

        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO reportlog (proctor, block, date, subject, room, start, end)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (proctor, block, date, subject, room, start, end)
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            logging.info("Report details inserted successfully")
        except Error as e:
            logging.error(f"Error inserting report details: {e}")

logging.basicConfig(level=logging.INFO)

db_manager = DatabaseManager()
