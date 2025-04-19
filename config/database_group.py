from PyQt6.QtWidgets import QGroupBox, QFormLayout, QLineEdit

class DatabaseGroupBox(QGroupBox):
    def __init__(self, host, user, password, database):
        super().__init__("Database")
        layout = QFormLayout(self)
        self.db_host = QLineEdit(host)
        self.db_user = QLineEdit(user)
        self.db_pass = QLineEdit(password)
        self.db_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.db_name = QLineEdit(database)
        layout.addRow("Host:", self.db_host)
        layout.addRow("User:", self.db_user)
        layout.addRow("Password:", self.db_pass)
        layout.addRow("Database:", self.db_name)

    def get_values(self):
        return {
            "host": self.db_host.text().strip(),
            "user": self.db_user.text().strip(),
            "password": self.db_pass.text(),
            "database": self.db_name.text().strip()
        }
