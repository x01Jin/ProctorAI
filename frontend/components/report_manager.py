from PyQt6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QPushButton, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal, QFileSystemWatcher
from backend.utils.gui_utils import GUIManager
from pathlib import Path

class ReportManagerDock(QDockWidget):
    pdf_generation_requested = pyqtSignal()

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.temp_dir = Path("tempcaptures")
        self.being_deleted = set()
        self.displayed_files = set()
        self._init_ui()
        self._init_file_watcher()

    def _init_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.image_container = QWidget()
        self.image_layout = QVBoxLayout(self.image_container)
        self.scroll_area.setWidget(self.image_container)
        layout.addWidget(self.scroll_area)
        self.pdf_button = QPushButton("Generate PDF Report")
        self.pdf_button.clicked.connect(lambda: self.pdf_generation_requested.emit())
        layout.addWidget(self.pdf_button)
        self.setWidget(container)
        self.setMinimumWidth(300)

    def _init_file_watcher(self):
        self.temp_dir.mkdir(exist_ok=True)
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPath(str(self.temp_dir))
        self.file_watcher.directoryChanged.connect(self._handle_directory_change)
        self._load_existing_images()

    def _load_existing_images(self):
        for file in self.temp_dir.glob("*.jpg"):
            GUIManager.add_image_label_to_layout(str(file), self.image_layout)

    def _handle_directory_change(self, path):
        current_files = {str(f) for f in self.temp_dir.glob("*.jpg")}
        self.displayed_files.clear()
        for i in range(self.image_layout.count()):
            widget = self.image_layout.itemAt(i).widget()
            if widget and not widget.isHidden() and hasattr(widget, 'image_path'):
                self.displayed_files.add(widget.image_path)
        new_files = current_files - self.displayed_files - self.being_deleted
        for file_path in new_files:
            if Path(file_path).exists():
                GUIManager.add_image_label_to_layout(file_path, self.image_layout)
                self.displayed_files.add(file_path)
        removed_files = self.displayed_files - current_files - self.being_deleted
        for file_path in removed_files:
            GUIManager.remove_image_from_layout(file_path, self.image_layout)
            self.displayed_files.discard(file_path)
        self.being_deleted = {f for f in self.being_deleted if Path(f).exists()}
        if new_files or removed_files:
            self.image_container.update()

    def cleanup(self):
        self.file_watcher.removePath(str(self.temp_dir))
        if self.temp_dir.exists():
            for file in self.temp_dir.iterdir():
                if file.is_file():
                    file.unlink()
