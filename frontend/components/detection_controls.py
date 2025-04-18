from PyQt6.QtWidgets import QDockWidget, QWidget, QHBoxLayout, QLabel, QComboBox, QSlider, QSizePolicy
from .buttons import AnimatedStateButton
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
        self._init_ui()

    def _init_ui(self):
        def add_pair(layout, label_text, widget, policy=None):
            label = QLabel(label_text)
            if policy:
                widget.setSizePolicy(policy, QSizePolicy.Policy.Fixed)
            layout.addWidget(label)
            layout.addWidget(widget)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(25)

        self.filter_combo = QComboBox()
        add_pair(layout, "Filter By:", self.filter_combo, QSizePolicy.Policy.Expanding)
        self.filter_combo.currentTextChanged.connect(lambda text: self.filter_changed.emit(text))

        self.capture_class_combo = QComboBox()
        add_pair(layout, "Capture:", self.capture_class_combo, QSizePolicy.Policy.Expanding)
        self.capture_class_combo.currentTextChanged.connect(lambda text: self.capture_class_changed.emit(text))

        self.display_mode_combo = QComboBox()
        self.display_mode_combo.addItems(["draw_labels", "draw_confidence"])
        add_pair(layout, "Display Mode:", self.display_mode_combo, QSizePolicy.Policy.Expanding)
        self.display_mode_combo.currentTextChanged.connect(lambda text: self.display_mode_changed.emit(text))

        self.detection_button = AnimatedStateButton("Start Detection")
        self.detection_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.detection_button.clicked.connect(lambda: self.detection_toggle_requested.emit())
        layout.addWidget(self.detection_button)

        self.confidence_label = QLabel("10%")
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(10)
        self.confidence_slider.setMinimumWidth(self.confidence_slider.sizeHint().width() * 3)
        self.confidence_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.confidence_slider.valueChanged.connect(self._update_confidence_label)

        confidence_container = QHBoxLayout()
        confidence_container.addWidget(QLabel("Confidence Threshold:"), 1)
        confidence_container.addWidget(self.confidence_label, 1)
        confidence_container.addWidget(self.confidence_slider, 3)
        confidence_widget = QWidget()
        confidence_widget.setLayout(confidence_container)
        confidence_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(confidence_widget)

        layout.addStretch(1)
        self.setWidget(container)

    def _update_confidence_label(self, value):
        self.confidence_label.setText(f"{value}%")
        self.confidence_changed.emit(value / 100.0)

    def update_model_classes(self, classes):
        current_text = self.capture_class_combo.currentText()
        self.capture_class_combo.clear()
        if classes:
            self.capture_class_combo.addItems(classes)
            if current_text in classes:
                self.capture_class_combo.setCurrentText(current_text)
        self._populate_filter_selection(classes)

    def _populate_filter_selection(self, classes):
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
        self.detection_button.set_active(is_running)
