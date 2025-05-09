from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
import hashlib

class LoginWindow(QDialog):
    def __init__(self, db_service, session_manager, parent=None):
        super().__init__(parent)
        self.db_service = db_service
        self.session_manager = session_manager
        self.setWindowTitle("Login")
        self.setFixedSize(320, 220)
        self.layout = QVBoxLayout(self)
        self.info_label = QLabel("Please log in to continue")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.info_label)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Proctor Name")
        self.layout.addWidget(self.username_input)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self._handle_login)
        self.layout.addWidget(self.login_button)
        self.setLayout(self.layout)

    def _handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return
        user = self.db_service.get_user_by_proctor_name(username)
        if not user or user.get("user_role") != "proctor":
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            return
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user["password"] != password_hash:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            return
        self.user_id = user["id"]
        self.proctor_name = user["proctor_name"]
        self.accept()

    def get_user(self):
        return self.username_input.text().strip()

    def get_user_id(self):
        return getattr(self, "user_id", None)

    def get_proctor_name(self):
        return getattr(self, "proctor_name", None)