from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QBrush, QTextCursor, QPalette
from backend.services.application_state import ApplicationState
from config.settings_manager import SettingsManager
from config.settings_dialog import SettingsDialog
from frontend.themes.theme_manager import ThemeManager
import time

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
        self._setup_ui()
        self._center_on_screen()
        self._log_message("Starting ProctorAI...", "info")

    def log_message(self, message, level="info"):
        self._log_message(message, level)

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _setup_ui(self):
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

    def _log_message(self, message, level="info"):
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

    def _check_config(self, on_complete):
        self._log_message("Checking configuration...")
        QTimer.singleShot(1000, lambda: self._finish_check_config(on_complete))

    def _finish_check_config(self, on_complete):
        settings = SettingsManager()
        if not settings.config_exists():
            self._log_message("No configuration file found...", "warning")
            self._log_message("Creating configuration file with default values...")
            settings.create_default_config()
            self._log_message("Configuration file created... launching setup...", "info")
            settings_dialog = SettingsDialog(settings, parent=self, setup_mode=True)
            if settings_dialog.exec() != SettingsDialog.DialogCode.Accepted:
                self._log_message("Setup cancelled... proceeding anyway...", "warning")
            QTimer.singleShot(100, lambda: on_complete(True))
        else:
            self._log_message("Configuration found", "success")
            QTimer.singleShot(100, lambda: on_complete(True))

    def _check_internet(self, on_complete, retry_count=3, attempt=0):
        self._log_message("Checking internet connection...")
        import subprocess
        import platform
        def try_ping():
            try:
                command = ["ping", "-n" if platform.system().lower()=="windows" else "-c", "1", "8.8.8.8"]
                subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                self._log_message("Internet connection established", "success")
                QTimer.singleShot(100, lambda: on_complete(True))
            except subprocess.CalledProcessError:
                if attempt < retry_count - 1:
                    self._log_message(f"Internet connection failed, retrying... ({attempt + 1}/{retry_count})", "warning")
                    QTimer.singleShot(1000, lambda: self._check_internet(on_complete, retry_count, attempt + 1))
                else:
                    self._log_message("Internet connection failed after 3 attempts", "error")
                    self._log_message("Some features may be limited without internet connection", "warning")
                    QTimer.singleShot(100, lambda: on_complete(False))
        QTimer.singleShot(1000, try_ping)

    def _check_roboflow(self, on_complete, retry_count=3, attempt=0):
        app_state = ApplicationState.get_instance()
        app_state.initialize_roboflow()
        rf = app_state.roboflow
        self._log_message("Checking Roboflow connection...")
        def try_roboflow():
            if rf.initialize(splash_screen=self):
                self._log_message("Roboflow connection established", "success")
                app_state.update_connection_status(roboflow=True)
                QTimer.singleShot(100, lambda: on_complete(True))
            else:
                if attempt < retry_count - 1:
                    self._log_message(f"Roboflow connection failed: {rf.last_error or 'Connection test failed'}, retrying... ({attempt + 1}/{retry_count})", "warning")
                    QTimer.singleShot(1000, lambda: self._check_roboflow(on_complete, retry_count, attempt + 1))
                else:
                    self._log_message("Opening setup to check the Roboflow settings...", "warning")
                    settings_dialog = SettingsDialog(SettingsManager(), parent=self, setup_mode=True, setup_type="roboflow")
                    if settings_dialog.exec() != SettingsDialog.DialogCode.Accepted:
                        self._log_message("Roboflow setup cancelled... exiting the application...", "error")
                        app_state.update_connection_status(roboflow=False)
                        QTimer.singleShot(1000, lambda: QApplication.instance().quit())
                        return
                    QTimer.singleShot(100, lambda: self._check_roboflow(on_complete, retry_count, attempt + 1))
        QTimer.singleShot(1000, try_roboflow)

    def _check_database(self, on_complete, retry_count=3, attempt=0):
        app_state = ApplicationState.get_instance()
        app_state.initialize_database()
        db = app_state.database
        self._log_message("Checking database connection...")
        def try_db():
            if db.test_connection():
                self._log_message("Database connection established", "success")
                app_state.update_connection_status(database=True)
                QTimer.singleShot(100, lambda: on_complete(True))
            else:
                if attempt < retry_count - 1:
                    self._log_message(f"Database connection failed: Connection test failed, retrying... ({attempt + 1}/{retry_count})", "warning")
                    QTimer.singleShot(1000, lambda: self._check_database(on_complete, retry_count, attempt + 1))
                else:
                    self._log_message("Opening setup to check the database settings...", "warning")
                    settings_dialog = SettingsDialog(SettingsManager(), parent=self, setup_mode=True, setup_type="database")
                    if settings_dialog.exec() != SettingsDialog.DialogCode.Accepted:
                        self._log_message("Database setup cancelled... exiting the application...", "error")
                        app_state.update_connection_status(database=False)
                        QTimer.singleShot(1000, lambda: QApplication.instance().quit())
                        return
                    QTimer.singleShot(100, lambda: self._check_database(on_complete, retry_count, attempt + 1))
        QTimer.singleShot(1000, try_db)

    def perform_checks(self, on_complete=None):
        ApplicationState.get_instance()
        self._check_config(lambda config_ok: self._after_config(config_ok, on_complete))

    def _after_config(self, config_ok, on_complete):
        self._check_internet(lambda internet_ok: self._after_internet(config_ok, internet_ok, on_complete))

    def _after_internet(self, config_ok, internet_ok, on_complete):
        self._check_roboflow(lambda roboflow_ok: self._after_roboflow(config_ok, internet_ok, roboflow_ok, on_complete))

    def _after_roboflow(self, config_ok, internet_ok, roboflow_ok, on_complete):
        self._check_database(lambda database_ok: self._after_database(config_ok, internet_ok, roboflow_ok, database_ok, on_complete))

    def _after_database(self, config_ok, internet_ok, roboflow_ok, database_ok, on_complete):
        self._log_message("All checks complete, starting application...", "info")
        QTimer.singleShot(3000, lambda: self._complete_checks(config_ok, internet_ok, roboflow_ok, database_ok, on_complete))

    def _complete_checks(self, config_ok, internet_ok, roboflow_ok, database_ok, on_complete):
        if on_complete:
            on_complete(config_ok, internet_ok, roboflow_ok, database_ok)
