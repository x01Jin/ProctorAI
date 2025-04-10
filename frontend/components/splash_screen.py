from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QBrush, QTextCursor, QPalette
import time
from backend.services.application_state import ApplicationState
from config.settings_manager import SettingsManager
from config.settings_dialog import SettingsDialog
from frontend.themes.theme_manager import ThemeManager

class SplashScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(600, 400)
        
        self.settings = SettingsManager()
        self.theme_manager = ThemeManager(self)
        theme = self.settings.get_setting("theme", "theme")
        if theme:
            self.theme_manager.apply_theme(theme)
            
        self.setProperty("class", "splash-screen")
        self.setStyleSheet("""
            QWidget[class="splash-screen"] {
                border: 2px solid palette(dark);
                border-radius: 10px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
            QTextEdit {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(dark);
                border-radius: 5px;
                padding: 5px;
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
        title_label.setStyleSheet("color: palette(text);")
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Cheating Detection Assistant")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: palette(text);")
        layout.addWidget(subtitle_label)
        
        thesis_label = QLabel("A Thesis Project")
        thesis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thesis_font = QFont()
        thesis_font.setPointSize(12)
        thesis_label.setFont(thesis_font)
        thesis_label.setStyleSheet("color: palette(text);")
        layout.addWidget(thesis_label)
        
        creators_label = QLabel("Created by: CROISSANTS")
        creators_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        creators_font = QFont()
        creators_font.setPointSize(10)
        creators_label.setFont(creators_font)
        creators_label.setStyleSheet("color: palette(text);")
        layout.addWidget(creators_label)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFixedHeight(200)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(dark);
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
            format.setForeground(QBrush(QColor(76, 175, 80)))
            prefix = "✓"
        elif level == "warning":
            format.setForeground(QBrush(QColor(255, 193, 7)))
            prefix = "⚠️"
        elif level == "error":
            format.setForeground(QBrush(QColor(244, 67, 54)))
            prefix = "❌"
        else:
            format.setForeground(QBrush(self.palette().color(QPalette.ColorRole.Text)))
            prefix = "→"
        
        self.log_display.moveCursor(QTextCursor.MoveOperation.End)
        self.log_display.textCursor().insertText(f"[{timestamp}] {prefix} {message}\n", format)
        self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())
        QApplication.processEvents()
        time.sleep(0.5)

    def check_config(self):
        self.log_message("Checking configuration...")
        QApplication.processEvents()
        time.sleep(1)
        
        settings = SettingsManager()
        if not settings.config_exists():
            self.log_message("No configuration file found...", "warning")
            self.log_message("Creating configuration file with default values...")
            settings.create_default_config()
            self.log_message("Configuration file created... launching setup...", "info")
            
            settings_dialog = SettingsDialog(settings, parent=self, setup_mode=True)
            if settings_dialog.exec() != SettingsDialog.DialogCode.Accepted:
                self.log_message("Setup cancelled... proceeding anyway...", "warning")
            return True
            
        self.log_message("Configuration found", "success")
        return True

    def check_internet(self, retry_count=3):
        self.log_message("Checking internet connection...")
        import subprocess
        import platform
        
        for attempt in range(retry_count):
            try:
                command = ["ping", "-n" if platform.system().lower()=="windows" else "-c", "1", "8.8.8.8"]
                subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                self.log_message("Internet connection established", "success")
                return True
            except subprocess.CalledProcessError:
                if attempt < retry_count - 1:
                    self.log_message(f"Internet connection failed, retrying... ({attempt + 1}/{retry_count})", "warning")
                else:
                    self.log_message("Internet connection failed after 3 attempts", "error")
                    self.log_message("Some features may be limited without internet connection", "warning")
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
                if rf.initialize(splash_screen=self):
                    self.log_message("Roboflow connection established", "success")
                    app_state.update_connection_status(roboflow=True)
                    return True
                raise Exception(rf.last_error or "Connection test failed")
            except Exception as e:
                if attempt < retry_count - 1:
                    self.log_message(f"Roboflow connection failed: {str(e)}, retrying... ({attempt + 1}/{retry_count})", "warning")
                else:
                    self.log_message("Opening setup to check the Roboflow settings...", "warning")
                    
                    settings_dialog = SettingsDialog(SettingsManager(), parent=self, setup_mode=True, setup_type="roboflow")
                    if settings_dialog.exec() != SettingsDialog.DialogCode.Accepted:
                        self.log_message("Roboflow setup cancelled... exiting the application...", "error")
                        app_state.update_connection_status(roboflow=False)
                        QTimer.singleShot(1000, lambda: QApplication.instance().quit())
                        return False
                    
                    return self.check_roboflow(retry_count)

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
                    self.log_message("Opening setup to check the database settings...", "warning")
                    
                    settings_dialog = SettingsDialog(SettingsManager(), parent=self, setup_mode=True, setup_type="database")
                    if settings_dialog.exec() != SettingsDialog.DialogCode.Accepted:
                        self.log_message("Database setup cancelled... exiting the application...", "error")
                        app_state.update_connection_status(database=False)
                        QTimer.singleShot(1000, lambda: QApplication.instance().quit())
                        return False
                    
                    return self.check_database(retry_count)

    def perform_checks(self, on_complete=None):
        # Initialize application state at the start
        ApplicationState.get_instance()
        
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
