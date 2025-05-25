import mysql.connector
from mysql.connector import Error
import logging

DB_LOGGER = logging.getLogger('database')

_connection = None
_last_error = None

def get_db_config():
    return {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'proctorai'
    }

def fetch_roboflow_settings():
    ensure_connection()
    if _connection is None:
        DB_LOGGER.error("Failed to fetch Roboflow settings: No database connection")
        return None
    try:
        with _connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT api_key, project, model_version, model_classes FROM modelapi ORDER BY updated_at DESC LIMIT 1"
            )
            settings = cursor.fetchone()
            if not settings:
                error_msg = "No Roboflow settings found in database"
                set_last_error(error_msg)
                DB_LOGGER.error(error_msg)
                return None
            return settings
    except Error as e:
        error_msg = str(e)
        set_last_error(error_msg)
        DB_LOGGER.error(f"Error fetching Roboflow settings: {error_msg}")
        return None

def set_last_error(msg):
    global _last_error
    _last_error = msg

def get_last_error():
    return _last_error

def connect():
    global _connection
    try:
        db_config = get_db_config()
        _connection = mysql.connector.connect(**db_config)
        if _connection.is_connected():
            db_info = _connection.get_server_info()
            session_id = _connection.connection_id
            DB_LOGGER.info(f"Connected to MySQL (Server: {db_info}, Session ID: {session_id})")
            return True
    except Error as e:
        error_msg = str(e)
        set_last_error(error_msg)
        DB_LOGGER.error(f"Error connecting to MySQL: {error_msg}")
        _connection = None
    return False

def ensure_connection():
    global _connection
    if _connection is None or not _connection.is_connected():
        DB_LOGGER.info("Attempting to reconnect...")
        connect()

def insert_report_details(user_id, block, date, subject, room, start, end, num_students):
    ensure_connection()
    if _connection is None:
        error_msg = "No database connection"
        set_last_error(error_msg)
        DB_LOGGER.error(f"Failed to insert report details: {error_msg}")
        return False
    try:
        session_id = _connection.connection_id
        DB_LOGGER.info(f"Beginning report details insert (Session ID: {session_id})")
        with _connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO reportlog (user_id, num_students, block, subject, room, start, end, date) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (user_id, int(num_students), block, subject, room, start, end, date)
            )
            _connection.commit()
            DB_LOGGER.info(f"Report details inserted successfully (Session ID: {session_id})")
            return True
    except (Error, ValueError) as e:
        error_msg = str(e)
        set_last_error(error_msg)
        DB_LOGGER.error(f"Failed to insert report details: {error_msg}")
        return False

def get_user_by_proctor_name(proctor_name):
    ensure_connection()
    if _connection is None:
        return None
    try:
        with _connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE proctor_name = %s AND user_role = 'proctor'",
                (proctor_name,)
            )
            return cursor.fetchone()
    except Error as e:
        DB_LOGGER.error(f"Error getting user by proctor name: {str(e)}")
        return None

def get_user_by_email(email):
    ensure_connection()
    if _connection is None:
        return None
    try:
        with _connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s AND user_role = 'proctor'",
                (email,)
            )
            return cursor.fetchone()
    except Error as e:
        DB_LOGGER.error(f"Error getting user by email: {str(e)}")
        return None

def get_user_by_id(user_id):
    ensure_connection()
    if _connection is None:
        return None
    try:
        with _connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )
            return cursor.fetchone()
    except Error as e:
        DB_LOGGER.error(f"Error getting user by ID: {str(e)}")
        return None

def update_user_profile(user_id, proctor_name, email, password_hash):
    ensure_connection()
    if _connection is None:
        return False
    try:
        with _connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE (proctor_name = %s OR email = %s) AND id != %s",
                (proctor_name, email, user_id)
            )
            if cursor.fetchone():
                set_last_error("Proctor name or email already exists")
                DB_LOGGER.error("Proctor name or email already exists")
                return False
            cursor.execute(
                "UPDATE users SET proctor_name = %s, email = %s, password = %s WHERE id = %s",
                (proctor_name, email, password_hash, user_id)
            )
            _connection.commit()
            return True
    except Error as e:
        DB_LOGGER.error(f"Error updating user profile: {str(e)}")
        return False
