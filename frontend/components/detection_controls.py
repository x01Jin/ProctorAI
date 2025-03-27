from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal

class DetectionControlsDock(QDockWidget):
    detection_toggle_requested = pyqtSignal()
    confidence_changed = pyqtSignal(float)
    display_mode_changed = pyqtSignal(str)
    capture_class_changed = pyqtSignal(str)
    filter_changed = pyqtSignal(str)

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAllowedAreas(Qt.DockWidgetArea.TopDockWidgetArea | Qt.DockWidgetArea.BottomDockWidgetArea)
        self.setup_ui()

    def setup_ui(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.setup_filter_combo(layout)

        self.setup_capture_combo(layout)

        self.setup_display_mode_combo(layout)

        self.setup_detection_button(layout)

        self.setup_confidence_slider(layout)

        self.setWidget(container)

    def setup_filter_combo(self, layout):
        self.filter_combo = QComboBox()
        layout.addWidget(QLabel("Filter By:"))
        layout.addWidget(self.filter_combo)
        self.filter_combo.currentTextChanged.connect(self.filter_changed.emit)

    def setup_capture_combo(self, layout):
        self.capture_class_combo = QComboBox()
        layout.addWidget(QLabel("Capture:"))
        layout.addWidget(self.capture_class_combo)
        self.capture_class_combo.currentTextChanged.connect(self.capture_class_changed.emit)

    def setup_display_mode_combo(self, layout):
        self.display_mode_combo = QComboBox()
        self.display_mode_combo.addItems(["draw_labels", "draw_confidence"])
        layout.addWidget(QLabel("Display Mode:"))
        layout.addWidget(self.display_mode_combo)
        self.display_mode_combo.currentTextChanged.connect(self.display_mode_changed.emit)

    def setup_detection_button(self, layout):
        self.detection_button = QPushButton("Start Detection")
        self.detection_button.clicked.connect(self.detection_toggle_requested.emit)
        layout.addWidget(self.detection_button)

    def setup_confidence_slider(self, layout):
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(10)
        self.confidence_label = QLabel("10%")

        layout.addWidget(QLabel("Confidence Threshold:"))
        layout.addWidget(self.confidence_label)
        layout.addWidget(self.confidence_slider)

        self.confidence_slider.valueChanged.connect(self.update_confidence_label)

    def update_confidence_label(self, value):
        self.confidence_label.setText(f"{value}%")
        self.confidence_changed.emit(value / 100.0)

    def update_model_classes(self, classes):
        # Update capture class combo box
        current_text = self.capture_class_combo.currentText()
        self.capture_class_combo.clear()
        if classes:
            self.capture_class_combo.addItems(classes)
            # Restore previous selection if it exists in new classes
            if current_text in classes:
                self.capture_class_combo.setCurrentText(current_text)
        
        # Update filter combo box
        self.populate_filter_selection(classes)

    def populate_filter_selection(self, classes):
        self.filter_combo.clear()
        self.filter_combo.addItem("All")
        if classes:
            self.filter_combo.addItems(classes)
        else:
            self.filter_combo.addItems(["No classes available"])

    def get_selected_capture_class(self):
        return self.capture_class_combo.currentText()

    def get_display_mode(self):
        return self.display_mode_combo.currentText()

    def get_confidence_threshold(self):
        return self.confidence_slider.value() / 100.0

    def update_detection_button_text(self, is_running):
        self.detection_button.setText("Stop Detection" if is_running else "Start Detection")
