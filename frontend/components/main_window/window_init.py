from PyQt6.QtWidgets import QSplitter, QDockWidget
from PyQt6.QtCore import Qt

def setup_window_geometry(window):
    screen = window.screen().availableGeometry()
    width = int(screen.width() * 0.9)
    height = int(screen.height() * 0.9)
    window.resize(width, height)
    window.move((screen.width() - width) // 2, (screen.height() - height) // 2)

def setup_window_layout(window):
    splitter = QSplitter(Qt.Orientation.Horizontal)
    window.camera_display.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
    window.report_manager.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
    window.detection_controls.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
    splitter.addWidget(window.camera_display)
    splitter.addWidget(window.report_manager)
    window.setCentralWidget(splitter)
    window.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, window.detection_controls)

def initialize_window(window):
    window.setWindowTitle("ProctorAI v1.4.1r by CROISSANTS")
    setup_window_geometry(window)
    setup_window_layout(window)
