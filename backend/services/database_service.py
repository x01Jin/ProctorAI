import mysql.connector
from mysql.connector import Error
import logging

DB_REQUIRED_FIELDS = ['host', 'user', 'database']
DB_LOGGER = logging.getLogger('database')

_connection = None
_last_error = None

def get_db_config(settings):
    db_settings = settings.get_setting('database')
    if not db_settings:
        set_last_error("Database settings not found")
        DB_LOGGER.error("Database settings not found")
        return None
    for field in DB_REQUIRED_FIELDS:
        if not db_settings.get(field):
            error_msg = f"Missing required database setting: {field}"
            set_last_error(error_msg)
            DB_LOGGER.error(error_msg)
            return None
    return {
        'host': db_settings['host'],
        'user': db_settings['user'],
        'password': db_settings.get('password', ''),
        'database': db_settings['database']
    }

def set_last_error(msg):
    global _last_error
    _last_error = msg

def get_last_error():
    return _last_error

def connect(settings):
    global _connection
    try:
        db_config = get_db_config(settings)
        if not db_config:
            return False
        _connection = mysql.connector.connect(**db_config)
        if _connection.is_connected():
            db_info = _connection.get_server_info()
            session_id = _connection.connection_id
            DB_LOGGER.info(f"Successfully connected to MySQL database (Server: {db_info}, Session ID: {session_id})")
            return True
    except Error as e:
        error_msg = str(e)
        set_last_error(error_msg)
        DB_LOGGER.error(f"Error connecting to MySQL: {error_msg}")
        _connection = None
    return False

def ensure_connection(settings):
    global _connection
    if _connection is None or not _connection.is_connected():
        DB_LOGGER.info("Attempting to reconnect...")
        connect(settings)

def insert_report_details(settings, proctor, block, date, subject, room, start, end, num_students):
    global _connection
    ensure_connection(settings)
    if _connection is None:
        error_msg = "No database connection"
        set_last_error(error_msg)
        DB_LOGGER.error(f"Failed to insert report details: {error_msg}")
        return
    try:
        session_id = _connection.connection_id
        DB_LOGGER.info(f"Beginning report details insert (Session ID: {session_id})")
        with _connection.cursor() as cursor:
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
            _connection.commit()
            DB_LOGGER.info(f"Report details inserted successfully (Session ID: {session_id})")
    except Error as e:
        error_msg = str(e)
        set_last_error(error_msg)
        DB_LOGGER.error(f"Error inserting report details (Session ID: {session_id if _connection else 'None'}): {error_msg}")
