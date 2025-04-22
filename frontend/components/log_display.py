from PyQt6.QtWidgets import QTextEdit, QApplication
from PyQt6.QtGui import QTextCharFormat, QColor, QBrush, QTextCursor
import time

class LogDisplay:
    def __init__(self):
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFixedHeight(200)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #181a20;
                color: #f5f6fa;
                border: 1px solid #444857;
                border-radius: 5px;
                padding: 5px;
            }
        """)

    def log(self, message, level="info"):
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
            format.setForeground(QBrush(QColor(245, 246, 250)))
            prefix = "→"
        self.text_edit.moveCursor(QTextCursor.MoveOperation.End)
        self.text_edit.textCursor().insertText(f"[{timestamp}] {prefix} {message}\n", format)
        self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
        QApplication.processEvents()

    def widget(self):
        return self.text_edit
