from PyQt6.QtWidgets import QLabel, QInputDialog, QMenu, QMessageBox
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt
import os

class ImageLabel(QLabel):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.tag = ""

    def show_context_menu(self, pos):
        context_menu = QMenu(self)
        delete_action = context_menu.addAction("Delete")
        edit_tag_action = context_menu.addAction("Edit Tag")
        action = context_menu.exec(self.mapToGlobal(pos))
        if action == delete_action:
            self.delete_image()
        elif action == edit_tag_action:
            self.add_tag()

    def delete_image(self):
        try:
            if os.path.exists(self.image_path):
                os.remove(self.image_path)
            self.deleteLater()
        except Exception as e:
            print(f"Error deleting image {self.image_path}: {e}")
            self.deleteLater()

    def add_tag(self):
        tag, ok = QInputDialog.getText(self, "Add Tag", "Enter tag:")
        if ok and tag:
            if self.is_valid_tag(tag):
                self.tag = tag
                self.setToolTip(tag)
                self.update()
                self.update_filename_with_tag()
            else:
                QMessageBox.critical(self, "Invalid Tag", "The tag contains invalid characters.")
    
    def redo_tag(self):
        self.add_tag()

    def is_valid_tag(self, tag):
        invalid_chars = r'<>:"/\|?*'
        return not any(char in invalid_chars for char in tag)

    def update_filename_with_tag(self):
        directory, original_filename = os.path.split(self.image_path)
        _, ext = os.path.splitext(original_filename)
        new_filename = f"{self.tag}{ext}"
        new_filepath = os.path.join(directory, new_filename)

        counter = 1
        while os.path.exists(new_filepath):
            new_filename = f"{self.tag}_{counter}{ext}"
            new_filepath = os.path.join(directory, new_filename)
            counter += 1

        os.rename(self.image_path, new_filepath)
        self.image_path = new_filepath

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.toolTip():
            painter = QPainter(self)
            painter.setPen(Qt.GlobalColor.red)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.toolTip())
