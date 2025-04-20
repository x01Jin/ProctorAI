from PyQt6.QtWidgets import QGroupBox, QFormLayout, QLineEdit

def create_database_group(host, user, password, database):
    group = QGroupBox("Database")
    layout = QFormLayout(group)
    db_host = QLineEdit(host)
    db_user = QLineEdit(user)
    db_pass = QLineEdit(password)
    db_pass.setEchoMode(QLineEdit.EchoMode.Password)
    db_name = QLineEdit(database)
    layout.addRow("Host:", db_host)
    layout.addRow("User:", db_user)
    layout.addRow("Password:", db_pass)
    layout.addRow("Database:", db_name)
    return group, {"host": db_host, "user": db_user, "password": db_pass, "database": db_name}

def get_database_values(widgets):
    return {
        "host": widgets["host"].text().strip(),
        "user": widgets["user"].text().strip(),
        "password": widgets["password"].text(),
        "database": widgets["database"].text().strip()
    }
