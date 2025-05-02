from PyQt6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QPushButton, QScrollArea, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QFileSystemWatcher
from pathlib import Path
import logging
from backend.utils.gui.image_label_manager import ImageLabelManager

class ReportManagerDock(QDockWidget):
    logger = logging.getLogger('report')
    pdf_generation_requested = pyqtSignal()

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.temp_dir = Path("tempcaptures")
        self._cleaned_up = False
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
        self._rebuild_image_layout()

    def _handle_directory_change(self, path):
        if self._cleaned_up:
            return
        self._rebuild_image_layout()

    def _rebuild_image_layout(self):
        if self._cleaned_up:
            return
        while self.image_layout.count():
            item = self.image_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        image_files = list(self.temp_dir.glob("*.jpg"))
        untagged = []
        tagged = []

        for file in image_files:
            name = file.stem
            if "_" in name or name.isalpha():
                tagged.append(file)
            else:
                untagged.append(file)

        untagged = sorted(untagged, key=lambda f: f.stat().st_mtime, reverse=True)
        tagged = sorted(tagged, key=lambda f: f.name.lower())

        latest_untagged = untagged[0] if untagged else None

        def trigger_update():
            self._rebuild_image_layout()

        for idx, file in enumerate(untagged):
            is_latest = (file == latest_untagged)
            ImageLabelManager.add_image_label_to_layout(
                str(file), self.image_layout, group="untagged", is_latest=is_latest, on_image_update=trigger_update
            )

        if untagged and tagged:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setFrameShadow(QFrame.Shadow.Sunken)
            sep.setStyleSheet("margin: 8px 0; border: 1px solid #888;")
            self.image_layout.addWidget(sep)

        for file in tagged:
            ImageLabelManager.add_image_label_to_layout(
                str(file), self.image_layout, group="tagged", is_latest=False, on_image_update=trigger_update
            )

        self.image_container.update()

    def update_image_list(self):
        self._rebuild_image_layout()

    def cleanup(self):
        self._cleaned_up = True
        try:
            self.file_watcher.directoryChanged.disconnect(self._handle_directory_change)
        except Exception as e:
            self.logger.error(f"Error disconnecting file watcher: {e}")
            pass
        self.file_watcher.removePath(str(self.temp_dir))
        if self.temp_dir.exists():
            for file in self.temp_dir.iterdir():
                if file.is_file():
                    file.unlink()
