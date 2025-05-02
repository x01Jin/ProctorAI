from PyQt6.QtWidgets import QLabel, QInputDialog, QMenu, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path

class ImageLabel(QLabel):
    tag_changed = pyqtSignal()
    image_deleted = pyqtSignal()

    def __init__(self, image_path, parent=None, filename_label=None):
        super().__init__(parent)
        self.image_path = str(image_path)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.tag = ""
        self.filename_label = filename_label

    def _show_context_menu(self, pos):
        context_menu = QMenu(self)
        actions = {
            "Delete": self._delete_image,
            "Edit Tag": self._add_tag
        }
        for name in actions:
            context_menu.addAction(name)
        action = context_menu.exec(self.mapToGlobal(pos))
        if action and action.text() in actions:
            actions[action.text()]()

    def _delete_image(self):
        parent = self.parent()
        while parent and not hasattr(parent, 'being_deleted'):
            parent = parent.parent()
        if parent:
            parent.being_deleted.add(self.image_path)
        self.deleteLater()
        path = Path(self.image_path)
        if path.exists():
            path.unlink()
        if parent:
            parent.being_deleted.discard(self.image_path)
        self.image_deleted.emit()

    def _add_tag(self):
        tag, ok = QInputDialog.getText(self, "Add Tag", "Enter tag:")
        if ok and tag and self._is_valid_tag(tag):
            self.tag = tag
            self.setToolTip(tag)
            self.update()
            self._update_filename_with_tag()
            self.tag_changed.emit()
            if self.filename_label and hasattr(self.filename_label, "parent"):
                parent = self.filename_label.parent()
                if hasattr(parent, "on_image_update") and callable(parent.on_image_update):
                    parent.on_image_update()
        elif ok and tag:
            QMessageBox.critical(self, "Invalid Tag", "The tag contains invalid characters.")

    def redo_tag(self):
        self._add_tag()

    def _is_valid_tag(self, tag):
        invalid_chars = r'<>:"/\|?*'
        return not any(char in invalid_chars for char in tag)

    def _update_filename_with_tag(self):
        path = Path(self.image_path)
        directory = path.parent
        ext = path.suffix
        filesystem_tag = self.tag.replace(' ', '_')
        new_filename = f"{filesystem_tag}{ext}"
        new_filepath = directory / new_filename
        counter = 1
        while new_filepath.exists():
            new_filename = f"{filesystem_tag}_{counter}{ext}"
            new_filepath = directory / new_filename
            counter += 1
        path.rename(new_filepath)
        self.image_path = str(new_filepath)
        if self.filename_label:
            display_name = self.tag if len(self.tag) <= 15 else self.tag[:15] + "..."
            self.filename_label.setText(display_name)
            self.filename_label.setToolTip(self.tag)
            self._update_filename_label_width()

    def _update_filename_label_width(self):
        if not self.filename_label:
            return
        metrics = self.filename_label.fontMetrics()
        text_width = metrics.horizontalAdvance(self.filename_label.text())
        max_width = self.window().width() * 0.8
        if text_width > max_width:
            elided_text = metrics.elidedText(self.filename_label.text(), Qt.TextElideMode.ElideRight, int(max_width))
            self.filename_label.setText(elided_text)
        self.filename_label.adjustSize()
