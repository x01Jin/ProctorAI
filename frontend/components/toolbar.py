from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QObject, pyqtSignal
import config.settings_manager as settings_manager
from config.settings_dialog import SettingsDialog
from backend.services.application_state import ApplicationState

class ToolbarManager(QObject):
    settings_updated = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.toolbar = QToolBar("Main Toolbar")
        self.settings_dialog = SettingsDialog(parent)
        parent.addToolBar(self.toolbar)
        self._setup_actions()

    def _setup_actions(self):
        actions = [
            ("Toggle Camera & Display", self._toggle_camera_display),
            ("Toggle Detection Controls", self._toggle_detection_controls),
            ("Toggle Captured Images Dock", self._toggle_report_manager),
            ("Settings", self._show_settings)
        ]
        for name, slot in actions:
            action = QAction(name, self.parent)
            action.triggered.connect(slot)
            self.toolbar.addAction(action)

    def _toggle_camera_display(self):
        self.parent.camera_display.setVisible(not self.parent.camera_display.isVisible())

    def _toggle_detection_controls(self):
        self.parent.detection_controls.setVisible(not self.parent.detection_controls.isVisible())

    def _toggle_report_manager(self):
        self.parent.report_manager.setVisible(not self.parent.report_manager.isVisible())

    def _show_settings(self):
        if self.settings_dialog.exec() == SettingsDialog.DialogCode.Accepted:
            theme = settings_manager.get_setting("theme", "theme")
            self.parent.theme_manager.apply_theme(theme)
            app_state = ApplicationState.get_instance()
            if app_state.database:
                app_state.database.connection = None
                connected = app_state.database.connect(settings_manager)
                app_state.update_connection_status(database=connected)
            self.settings_updated.emit()