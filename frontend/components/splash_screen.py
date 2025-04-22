from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from backend.services.application_state import ApplicationState
from frontend.components.log_display import LogDisplay
from backend.utils.check_utils import run_checks

class SplashScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(600, 400)
        self.setProperty("class", "splash-screen")
        self.setStyleSheet("""
            QWidget[class="splash-screen"] {
                background-color: #23272e;
                border: 2px solid #444857;
                border-radius: 10px;
            }
            QLabel {
                background: transparent;
                border: none;
                color: #f5f6fa;
            }
        """)
        self.log_display = LogDisplay()
        self._setup_ui()
        self._center_on_screen()
        self.log_display.log("Starting ProctorAI...", "info")

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
        title_label.setStyleSheet("color: #f5f6fa;")
        layout.addWidget(title_label)
        subtitle_label = QLabel("Cheating Detection Assistant")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #f5f6fa;")
        layout.addWidget(subtitle_label)
        thesis_label = QLabel("A Thesis Project")
        thesis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thesis_font = QFont()
        thesis_font.setPointSize(12)
        thesis_label.setFont(thesis_font)
        thesis_label.setStyleSheet("color: #f5f6fa;")
        layout.addWidget(thesis_label)
        creators_label = QLabel("Created by: CROISSANTS")
        creators_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        creators_font = QFont()
        creators_font.setPointSize(10)
        creators_label.setFont(creators_font)
        creators_label.setStyleSheet("color: #f5f6fa;")
        layout.addWidget(creators_label)
        layout.addWidget(self.log_display.widget())
        self.setLayout(layout)

    def perform_checks(self, on_complete=None):
        ApplicationState.get_instance()
        run_checks(
            log_display=self.log_display,
            on_complete=on_complete
        )
