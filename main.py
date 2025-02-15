import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QDockWidget, QLabel, QPushButton,
    QComboBox, QVBoxLayout, QHBoxLayout, QScrollArea,
    QStatusBar, QToolBar, QMessageBox, QDialog, QSlider,
    QApplication, QSplitter
)
from roboflow import Roboflow
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor, QAction
import os
from backend.services.database_service import db_manager
from config.settings import Settings, SettingsDialog
from backend.controllers.camera_controller import CameraManager
from backend.controllers.detection_controller import DetectionManager
from backend.controllers.report_controller import PDFReport
from backend.utils.gui_utils import GUIManager

MODEL_CLASSES = ["cheating", "not_cheating"]

def initialize_roboflow():
    try:
        settings = Settings()
        rf = Roboflow(api_key=settings.get_setting("roboflow", "api_key"))
        project = rf.workspace().project(settings.get_setting("roboflow", "project"))
        model = project.version(settings.get_setting("roboflow", "model_version")).model
        classes = MODEL_CLASSES
        return model, classes
    except Exception as e:
        print(f"Error initializing Roboflow: {e}")
        return None, []


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProctorAI")
        self.setGeometry(100, 100, 1280, 720)
        
        settings = Settings()
        if settings.get_setting("theme") == "dark":
            self.setupDarkPallete()
        else:
            self.setupLightPallete()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setupDocks()
        self.setupStatusBar()
        self.setupTimers()
        self.setupToolbar()

        model, classes = initialize_roboflow()
        if model is None:
            QMessageBox.critical(self, "Error", "Failed to initialize Roboflow model.")
            sys.exit(1)

        self.camera_manager = CameraManager(self)
        self.detection_manager = DetectionManager(model, self)

        self.populate_filter_selection(classes)

        self.camera_manager.frame_ready.connect(self.update_display)
        self.detection_manager.detections_ready.connect(self.update_detections)
        
        self.startCameraButton.clicked.connect(self.toggle_camera)
        self.startDetectionButton.clicked.connect(self.toggle_detection)
        self.generatePdfButton.clicked.connect(PDFReport.save_pdf)

    def populate_filter_selection(self, classes):
        self.filterCombo.clear()
        self.filterCombo.addItem("All")
        if classes:
            self.filterCombo.addItems(classes)
        else:
            self.filterCombo.addItems(["No classes available"])
        
    def setupDarkPallete(self):
        dark_pallete = QPalette()
        dark_pallete.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_pallete.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_pallete.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        dark_pallete.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_pallete.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_pallete.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_pallete.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_pallete.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_pallete.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_pallete.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_pallete.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(dark_pallete)
    
    def setupLightPallete(self):
        light_pallete = QPalette()
        light_pallete.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        light_pallete.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
        light_pallete.setColor(QPalette.ColorRole.Base, QColor(245, 245, 245))
        light_pallete.setColor(QPalette.ColorRole.AlternateBase, QColor(255, 255, 255))
        light_pallete.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
        light_pallete.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
        light_pallete.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
        light_pallete.setColor(QPalette.ColorRole.Button, QColor(255, 255, 255))
        light_pallete.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
        light_pallete.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        light_pallete.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        self.setPalette(light_pallete)

    def setupDocks(self):
        self.previewDock = QDockWidget("Camera and Display", self)
        self.previewDock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        camera_display_container = self.cameraDisplayDock()
        self.previewDock.setWidget(camera_display_container)

        self.reportDock = QDockWidget("Captured Images", self)
        self.reportDock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        report_manager_container = self.reportManagerDock()
        self.reportDock.setWidget(report_manager_container)

        self.controlsDock = QDockWidget("Detection Controls", self)
        self.controlsDock.setAllowedAreas(Qt.DockWidgetArea.TopDockWidgetArea | Qt.DockWidgetArea.BottomDockWidgetArea)
        detection_controls_container = self.detectionControlsDock()
        self.controlsDock.setWidget(detection_controls_container)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.previewDock)
        splitter.addWidget(self.reportDock)
        self.setCentralWidget(splitter)

        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.controlsDock)

    def cameraDisplayDock(self):
        camera_display_container = QWidget()
        camera_display_layout = QVBoxLayout(camera_display_container)
        camera_display_layout.setContentsMargins(10, 10, 10, 10)
        camera_display_layout.setSpacing(10)

        camera_controls_layout = QHBoxLayout()
        self.cameraCombo = QComboBox()
        camera_controls_layout.addWidget(QLabel("Select Camera:"))
        camera_controls_layout.addWidget(self.cameraCombo)

        self.startCameraButton = QPushButton("Start Camera")
        camera_controls_layout.addWidget(self.startCameraButton)

        display_label_layout = QVBoxLayout()
        self.displayLabel = QLabel()
        self.displayLabel.setFixedSize(640, 480)
        self.displayLabel.setStyleSheet("background-color: black; border: 2px solid #444444;")
        display_label_layout.addWidget(self.displayLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        camera_display_layout.addLayout(camera_controls_layout)
        camera_display_layout.addLayout(display_label_layout)

        return camera_display_container

    def reportManagerDock(self):
        report_manager_dock = QWidget()
        report_manager_layout = QVBoxLayout(report_manager_dock)
        report_manager_layout.setContentsMargins(10, 10, 10, 10)
        report_manager_layout.setSpacing(10)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.imageContainer = QWidget()
        self.imageLayout = QVBoxLayout(self.imageContainer)
        self.scrollArea.setWidget(self.imageContainer)

        report_manager_layout.addWidget(self.scrollArea)

        self.generatePdfButton = QPushButton("Generate PDF Report")
        report_manager_layout.addWidget(self.generatePdfButton)

        report_manager_dock.setMinimumWidth(300)

        return report_manager_dock
    
    def detectionControlsDock(self):
        detection_controls_container = QWidget()
        detection_controls_layout = QHBoxLayout(detection_controls_container)
        detection_controls_layout.setContentsMargins(10, 10, 10, 10)
        detection_controls_layout.setSpacing(10)

        self.filterCombo = QComboBox()
        detection_controls_layout.addWidget(QLabel("Filter By:"))
        detection_controls_layout.addWidget(self.filterCombo)

        self.captureClassCombo = QComboBox()
        self.captureClassCombo.addItems(MODEL_CLASSES)
        detection_controls_layout.addWidget(QLabel("Capture:"))
        detection_controls_layout.addWidget(self.captureClassCombo)

        self.displayModeCombo = QComboBox()
        self.displayModeCombo.addItems(["draw_labels", "draw_confidence"])
        detection_controls_layout.addWidget(QLabel("Display Mode:"))
        detection_controls_layout.addWidget(self.displayModeCombo)

        self.startDetectionButton = QPushButton("Start Detection")
        detection_controls_layout.addWidget(self.startDetectionButton)

        self.confidenceSlider = QSlider(Qt.Orientation.Horizontal)
        self.confidenceSlider.setRange(0, 100)
        self.confidenceSlider.setValue(10)
        self.confidenceLabel = QLabel("10%")
        detection_controls_layout.addWidget(QLabel("Confidence Threshold:"))
        detection_controls_layout.addWidget(self.confidenceLabel)
        detection_controls_layout.addWidget(self.confidenceSlider)

        self.confidenceSlider.valueChanged.connect(self.update_confidence_label)

        return detection_controls_container
    
    def get_selected_capture_class(self):
        selected_class = self.captureClassCombo.currentText()
        return selected_class

    def update_confidence_label(self, value):
        self.confidenceLabel.setText(f"{value}%")

    def setupStatusBar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.detectedObjectsLabel = QLabel("Detected Objects: 0")
        self.statusBar.addWidget(self.detectedObjectsLabel)

        self.internetStatusLabel = QLabel("Internet: Checking")
        self.databaseStatusLabel = QLabel("Database: Checking")
        self.statusBar.addPermanentWidget(self.internetStatusLabel)
        self.statusBar.addPermanentWidget(self.databaseStatusLabel)

        GUIManager.update_status(self.internetStatusLabel, self.databaseStatusLabel)

    def setupTimers(self):
        self.internetStatusTimer = QTimer(self)
        self.internetStatusTimer.timeout.connect(lambda: GUIManager.update_internet_status(self.internetStatusLabel))
        self.internetStatusTimer.start(1000)

        self.databaseStatusTimer = QTimer(self)
        self.databaseStatusTimer.timeout.connect(lambda: GUIManager.update_database_status(self.databaseStatusLabel))
        self.databaseStatusTimer.start(1000)

    def setupToolbar(self):
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)

        toggle_cnd_action = QAction("Toggle Camera & Display", self)
        toggle_cnd_action.triggered.connect(self.toggleCameraDisplayDock)
        self.toolbar.addAction(toggle_cnd_action)

        toggle_dc_action = QAction("Toggle Detection Controls", self)
        toggle_dc_action.triggered.connect(self.toggleDetectionControlsDock)
        self.toolbar.addAction(toggle_dc_action)

        toggle_rm_action = QAction("Toggle Captured Images Dock", self)
        toggle_rm_action.triggered.connect(self.toggleReportManagerDock)
        self.toolbar.addAction(toggle_rm_action)
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        self.toolbar.addAction(settings_action)

    def show_settings(self):
        settings = Settings()
        dialog = SettingsDialog(settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.setupDarkPallete() if settings.get_setting("theme") == "dark" else self.setupLightPallete()
            db_manager.connection = None
            db_manager.connect()

    def toggleCameraDisplayDock(self):
        self.previewDock.setVisible(not self.previewDock.isVisible())

    def toggleDetectionControlsDock(self):
        self.controlsDock.setVisible(not self.controlsDock.isVisible())

    def toggleReportManagerDock(self):
        self.reportDock.setVisible(not self.reportDock.isVisible())

    def toggle_camera(self):
        self.camera_manager.toggle_camera()

    def toggle_detection(self):
        self.detection_manager.toggle_detection()

    def update_display(self, frame):
        GUIManager.display_frame(frame, self.displayLabel, self)

    def update_detections(self, detections):
        self.detectedObjectsLabel.setText(f"Detected Objects: {len(detections)}")
        GUIManager.display_captures(detections, self.imageLayout, self)
    
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit Confirmation',
                                     "Are you sure you want to exit?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            GUIManager.cleanup(self)
            GUIManager.refresh_captures(self.imageLayout)
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    if not os.path.exists("tempcaptures"):
        os.makedirs("tempcaptures")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    
    window.show()
    sys.exit(app.exec())
