from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QPushButton,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QFileSystemWatcher
from backend.utils.gui_utils import GUIManager
import os
import logging

class ReportManagerDock(QDockWidget):
    pdf_generation_requested = pyqtSignal()

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.logger = logging.getLogger('report')
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.temp_dir = "tempcaptures"
        self.setup_ui()
        self.setup_file_watcher()

    def setup_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.setup_scroll_area(layout)
        self.setup_pdf_button(layout)
        self.setWidget(container)
        self.setMinimumWidth(300)

    def setup_scroll_area(self, layout):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.image_container = QWidget()
        self.image_layout = QVBoxLayout(self.image_container)
        self.scroll_area.setWidget(self.image_container)
        
        layout.addWidget(self.scroll_area)

    def setup_pdf_button(self, layout):
        self.pdf_button = QPushButton("Generate PDF Report")
        self.pdf_button.clicked.connect(self.pdf_generation_requested.emit)
        layout.addWidget(self.pdf_button)

    def setup_file_watcher(self):
        try:
            if not os.path.exists(self.temp_dir):
                os.makedirs(self.temp_dir)
                self.logger.info(f"Created directory: {self.temp_dir}")
            
            self.file_watcher = QFileSystemWatcher()
            success = self.file_watcher.addPath(self.temp_dir)
            if success:
                self.logger.info(f"File watcher started for {self.temp_dir}")
            else:
                self.logger.error(f"Failed to add path to file watcher: {self.temp_dir}")
                
            self.file_watcher.directoryChanged.connect(self.handle_directory_change)
            self.load_existing_images()
            
        except Exception as e:
            self.logger.error(f"Failed to set up file watcher: {e}")

    def load_existing_images(self):
        if os.path.exists(self.temp_dir):
            for filename in os.listdir(self.temp_dir):
                if filename.endswith('.jpg'):
                    image_path = os.path.join(self.temp_dir, filename)
                    GUIManager.add_image_label_to_layout(image_path, self.image_layout)

    def handle_directory_change(self, path):
        try:
            self.logger.info(f"Handling directory change in {path}")
            
            current_files = set()
            if os.path.exists(self.temp_dir):
                current_files = {os.path.join(self.temp_dir, f) for f in os.listdir(self.temp_dir) if f.endswith('.jpg')}

            displayed_files = set()
            for i in range(self.image_layout.count()):
                try:
                    widget = self.image_layout.itemAt(i).widget()
                    if widget and not widget.isHidden() and hasattr(widget, 'image_path'):
                        displayed_files.add(widget.image_path)
                except (RuntimeError, AttributeError) as e:
                    self.logger.error(f"Error accessing widget: {e}")
                    continue

            new_files = current_files - displayed_files
            removed_files = displayed_files - current_files

            if new_files:
                self.logger.info(f"Adding new files: {new_files}")
                for file_path in new_files:
                    try:
                        GUIManager.add_image_label_to_layout(file_path, self.image_layout)
                    except Exception as e:
                        self.logger.error(f"Failed to add image {file_path}: {e}")

            if removed_files:
                self.logger.info(f"Removing files: {removed_files}")
                for file_path in removed_files:
                    try:
                        GUIManager.remove_image_from_layout(file_path, self.image_layout)
                    except Exception as e:
                        self.logger.error(f"Failed to remove image {file_path}: {e}")

            if new_files or removed_files:
                self.image_container.update()
                
        except Exception as e:
            self.logger.error(f"Error in handle_directory_change: {e}")

    def cleanup(self):
        try:
            self.file_watcher.removePath(self.temp_dir)
            if os.path.exists(self.temp_dir):
                for file in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, file)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        self.logger.error(f"Error deleting {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Error in cleanup: {e}")
