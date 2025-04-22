from PyQt6.QtGui import QTextCharFormat, QColor, QBrush, QTextCursor
from PyQt6.QtWidgets import QApplication
import time

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
        format.setForeground(QBrush(QColor(245, 246, 250)))
        prefix = "→"
    self.log_display.moveCursor(QTextCursor.MoveOperation.End)
    self.log_display.textCursor().insertText(f"[{timestamp}] {prefix} {message}\n", format)
    self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())
    QApplication.processEvents()