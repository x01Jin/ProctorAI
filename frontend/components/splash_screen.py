from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QBrush, QTextCursor
import time
import urllib.request
from backend.services.application_state import ApplicationState

class SplashScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(600, 400)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 #2B2B2B,
                    stop: 1 #1E1E1E
                );
                border: 2px solid #404040;
                border-radius: 10px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
            QTextEdit {
                background-color: rgba(0, 0, 0, 0.3);
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 5px;
                selection-background-color: #404040;
            }
        """)
        self.setup_ui()
        self.center_on_screen()
        self.log_message("Starting ProctorAI...", "info")
    
    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        title_label = QLabel("Proctor AI")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Cheating Detection Assistant")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #E0E0E0;")
        layout.addWidget(subtitle_label)
        
        thesis_label = QLabel("A Thesis Project")
        thesis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thesis_font = QFont()
        thesis_font.setPointSize(12)
        thesis_label.setFont(thesis_font)
        thesis_label.setStyleSheet("color: #BDBDBD;")
        layout.addWidget(thesis_label)
        
        creators_label = QLabel("Created by: CROISSANTS")
        creators_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        creators_font = QFont()
        creators_font.setPointSize(10)
        creators_label.setFont(creators_font)
        creators_label.setStyleSheet("color: #9E9E9E;")
        layout.addWidget(creators_label)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFixedHeight(200)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.log_display)
        
        self.setLayout(layout)
        
    def log_message(self, message, level="info"):
        timestamp = time.strftime("%H:%M:%S")
        format = QTextCharFormat()
        
        if level == "success":
            format.setForeground(QBrush(QColor("#4CAF50")))
            prefix = "✓"
        elif level == "warning":
            format.setForeground(QBrush(QColor("#FFC107")))
            prefix = "⚠️"
        elif level == "error":
            format.setForeground(QBrush(QColor("#F44336")))
            prefix = "❌"
        else:
            format.setForeground(QBrush(QColor("#FFFFFF")))
            prefix = "→"
        
        self.log_display.moveCursor(QTextCursor.MoveOperation.End)
        self.log_display.textCursor().insertText(f"[{timestamp}] {prefix} {message}\n", format)
        self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())
        QApplication.processEvents()
        time.sleep(0.5)

    def check_config(self):
        from config.settings_manager import SettingsManager
        self.log_message("Checking configuration...")
        QApplication.processEvents()
        time.sleep(1)
        try:
            settings = SettingsManager()
            settings.validate_settings()
            self.log_message("Configuration found and valid", "success")
            return True
        except ValueError:
            self.log_message("No configuration found", "warning")
            return False
        except Exception as e:
            self.log_message(f"Error checking configuration: {str(e)}", "error")
            return False

    def check_internet(self, retry_count=3):
        app_state = ApplicationState.get_instance()
        self.log_message("Checking internet connection...")
        QApplication.processEvents()
        time.sleep(1)
        for attempt in range(retry_count):
            try:
                urllib.request.urlopen("http://google.com", timeout=1)
                self.log_message("Internet connection established", "success")
                app_state.update_connection_status(internet=True)
                return True
            except Exception as e:
                if attempt < retry_count - 1:
                    self.log_message(f"Internet connection failed ({str(e)}), retrying... ({attempt + 1}/{retry_count})", "warning")
                else:
                    self.log_message(f"Internet connection failed after 3 attempts: {str(e)}", "error")
                    app_state.update_connection_status(internet=False)
                    return False

    def check_roboflow(self, retry_count=3):
        app_state = ApplicationState.get_instance()
        app_state.initialize_roboflow()
        rf = app_state.roboflow
        
        self.log_message("Checking Roboflow connection...")
        QApplication.processEvents()
        time.sleep(1)
        for attempt in range(retry_count):
            try:
                self.log_message("loading Roboflow workspace...")
                QApplication.processEvents()
                time.sleep(1)
                self.log_message("loading Roboflow project...")
                QApplication.processEvents()
                time.sleep(1)
                if rf.initialize():
                    self.log_message("Roboflow connection established", "success")
                    app_state.update_connection_status(roboflow=True)
                    return True
                raise Exception(rf.last_error or "Connection test failed")
            except Exception as e:
                if attempt < retry_count - 1:
                    self.log_message(f"Roboflow connection failed: {str(e)}, retrying... ({attempt + 1}/{retry_count})", "warning")
                else:
                    self.log_message(f"Roboflow connection failed after 3 attempts: {str(e)}", "error")
                    app_state.update_connection_status(roboflow=False)
                    return False

    def check_database(self, retry_count=3):
        app_state = ApplicationState.get_instance()
        app_state.initialize_database()
        db = app_state.database
        
        self.log_message("Checking database connection...")
        QApplication.processEvents()
        time.sleep(1)
        for attempt in range(retry_count):
            try:
                if db.test_connection():
                    self.log_message("Database connection established", "success")
                    app_state.update_connection_status(database=True)
                    return True
                raise Exception("Connection test failed")
            except Exception as e:
                if attempt < retry_count - 1:
                    self.log_message(f"Database connection failed: {str(e)}, retrying... ({attempt + 1}/{retry_count})", "warning")
                else:
                    self.log_message(f"Database connection failed after 3 attempts: {str(e)}", "error")
                    app_state.update_connection_status(database=False)
                    return False

    def perform_checks(self, on_complete=None):
        config_ok = self.check_config()
        QTimer.singleShot(100, lambda: self._check_internet(config_ok, on_complete))

    def _check_internet(self, config_ok, on_complete):
        internet_ok = self.check_internet()
        QTimer.singleShot(100, lambda: self._check_roboflow(config_ok, internet_ok, on_complete))

    def _check_roboflow(self, config_ok, internet_ok, on_complete):
        roboflow_ok = self.check_roboflow()
        QTimer.singleShot(100, lambda: self._check_database(config_ok, internet_ok, roboflow_ok, on_complete))

    def _check_database(self, config_ok, internet_ok, roboflow_ok, on_complete):
        database_ok = self.check_database()
        
        self.log_message("All checks complete, starting application...", "info")
        QTimer.singleShot(3000, lambda: self._complete_checks(config_ok, internet_ok, roboflow_ok, database_ok, on_complete))

    def _complete_checks(self, config_ok, internet_ok, roboflow_ok, database_ok, on_complete):
        if on_complete:
            on_complete(config_ok, internet_ok, roboflow_ok, database_ok)
