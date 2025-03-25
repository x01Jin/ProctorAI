from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QAction
from config.settings_manager import SettingsManager
from config.settings_dialog import SettingsDialog
from backend.services.application_state import ApplicationState

class ToolbarManager:
    def __init__(self, parent):
        self.parent = parent
        self.toolbar = QToolBar("Main Toolbar")
        parent.addToolBar(self.toolbar)
        self.setup_actions()

    def setup_actions(self):
        toggle_camera_action = QAction("Toggle Camera & Display", self.parent)
        toggle_camera_action.triggered.connect(self.toggle_camera_display)
        self.toolbar.addAction(toggle_camera_action)

        toggle_controls_action = QAction("Toggle Detection Controls", self.parent)
        toggle_controls_action.triggered.connect(self.toggle_detection_controls)
        self.toolbar.addAction(toggle_controls_action)

        toggle_report_action = QAction("Toggle Captured Images Dock", self.parent)
        toggle_report_action.triggered.connect(self.toggle_report_manager)
        self.toolbar.addAction(toggle_report_action)

        settings_action = QAction("Settings", self.parent)
        settings_action.triggered.connect(self.show_settings)
        self.toolbar.addAction(settings_action)

    def toggle_camera_display(self):
        self.parent.camera_display.setVisible(
            not self.parent.camera_display.isVisible()
        )

    def toggle_detection_controls(self):
        self.parent.detection_controls.setVisible(
            not self.parent.detection_controls.isVisible()
        )

    def toggle_report_manager(self):
        self.parent.report_manager.setVisible(
            not self.parent.report_manager.isVisible()
        )

    def show_settings(self):
        settings = SettingsManager()
        dialog = SettingsDialog(settings, self.parent)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            theme = settings.get_setting("theme", "theme")
            self.parent.theme_manager.apply_theme(theme)
            
            app_state = ApplicationState.get_instance()
            if app_state.database:
                app_state.database.connection = None
                app_state.database.connect()
                app_state.update_connection_status(database=app_state.database.test_connection())
