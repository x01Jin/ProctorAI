from PyQt6.QtWidgets import QLabel, QInputDialog, QMenu, QMessageBox
from PyQt6.QtCore import Qt
import os

class ImageLabel(QLabel):
    def __init__(self, image_path, parent=None, filename_label=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.tag = ""
        self.filename_label = filename_label

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
            # Get the report manager instance
            parent = self.parent()
            while parent and not hasattr(parent, 'being_deleted'):
                parent = parent.parent()
            
            if parent:
                # Mark file as being deleted
                parent.being_deleted.add(self.image_path)
            
            # Remove UI first for responsiveness
            self.deleteLater()
            
            # Then delete file
            if os.path.exists(self.image_path):
                os.remove(self.image_path)
                
            if parent:
                # Remove from tracking set after deletion
                parent.being_deleted.discard(self.image_path)
        except Exception as e:
            print(f"Error deleting image {self.image_path}: {e}")
            if parent:
                parent.being_deleted.discard(self.image_path)

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
        if self.filename_label:
            self.filename_label.setText(self.tag)
            self.update_filename_label_width()

    def update_filename_label_width(self):
        if not self.filename_label:
            return
        metrics = self.filename_label.fontMetrics()
        text_width = metrics.horizontalAdvance(self.filename_label.text())
        max_width = self.window().width() * 0.8
        if text_width > max_width:
            elided_text = metrics.elidedText(self.filename_label.text(), Qt.TextElideMode.ElideRight, int(max_width))
            self.filename_label.setText(elided_text)
        self.filename_label.adjustSize()
