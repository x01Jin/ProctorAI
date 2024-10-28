import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QSlider, QStatusBar, QDockWidget, 
    QToolBar, QAction, QSplitter, QScrollArea, QDialog, QFileDialog, QLineEdit, QDateEdit, QMessageBox
)
from roboflow import Roboflow
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QDate, QObject, QTimer
from PyQt5.QtGui import QPalette, QColor, QPixmap, QImage
from pygrabber.dshow_graph import FilterGraph
import cv2
import os
from dbc import db_manager
import shutil
from datetime import datetime
import requests
from fpdf import FPDF

MODEL_CLASSES = ["cheating", "not_cheating"]

def initialize_roboflow():
    try:
        rf = Roboflow(api_key="Ig1F9Y1p5qSulNYEAxwb")
        project = rf.workspace().project("giam_sat_gian_lan")
        model = project.version(2).model
        classes = MODEL_CLASSES
        return model, classes
    except Exception as e:
        print(f"Error initializing Roboflow: {e}")
        return None, []


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProctorAI")
        self.setGeometry(100, 100, 1000, 700)
        
        self.setupDarkPallete()

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
        dark_pallete.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_pallete.setColor(QPalette.WindowText, Qt.white)
        dark_pallete.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_pallete.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_pallete.setColor(QPalette.ToolTipBase, Qt.white)
        dark_pallete.setColor(QPalette.ToolTipText, Qt.white)
        dark_pallete.setColor(QPalette.Text, Qt.white)
        dark_pallete.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_pallete.setColor(QPalette.ButtonText, Qt.white)
        dark_pallete.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_pallete.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(dark_pallete)

    def setupDocks(self):
        self.previewDock = QDockWidget("Camera and Display", self)
        self.previewDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        camera_display_container = self.cameraDisplayDock()
        self.previewDock.setWidget(camera_display_container)

        self.reportDock = QDockWidget("Captured Images", self)
        self.reportDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        report_manager_container = self.reportManagerDock()
        self.reportDock.setWidget(report_manager_container)

        self.controlsDock = QDockWidget("Detection Controls", self)
        self.controlsDock.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        detection_controls_container = self.detectionControlsDock()
        self.controlsDock.setWidget(detection_controls_container)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.previewDock)
        splitter.addWidget(self.reportDock)
        self.setCentralWidget(splitter)

        self.addDockWidget(Qt.TopDockWidgetArea, self.controlsDock)

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
        display_label_layout.addWidget(self.displayLabel, alignment=Qt.AlignCenter)

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

        self.confidenceSlider = QSlider(Qt.Horizontal)
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
        GUIManager.display_frame(frame, self.displayLabel)

    def update_detections(self, detections):
        self.detectedObjectsLabel.setText(f"Detected Objects: {len(detections)}")
        GUIManager.display_captures(detections, self.imageLayout)
    
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit Confirmation',
                                    "Are you sure you want to exit?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            GUIManager.cleanup()
            event.accept()
        else:
            event.ignore()


class CameraManager(QObject):
    frame_ready = pyqtSignal(object)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.camera_active = False
        self.cap = None
        self.current_image = None
        self.camera_devices = self.list_cameras()
        self.selected_camera = self.camera_devices[0] if self.camera_devices else ''
        self.camera_thread = None

        self.main_window.cameraCombo.currentIndexChanged.connect(self.on_camera_selected)

    def list_cameras(self):
        graph = FilterGraph()
        devices = graph.get_input_devices()
        self.main_window.cameraCombo.addItems(devices)
        return devices

    def on_camera_selected(self, index):
        self.selected_camera = self.camera_devices[index]

    def toggle_camera(self):
        self.camera_active = not self.camera_active
        if self.camera_active:
            self.main_window.startCameraButton.setText("Stop Camera")
            self.use_camera()
        else:
            self.main_window.startCameraButton.setText("Start Camera")
            self.stop_camera()

    def use_camera(self):
        camera_index = self.camera_devices.index(self.selected_camera)
        self.cap = cv2.VideoCapture(camera_index)
        if self.cap.isOpened():
            self.camera_thread = QThread()
            self.camera_thread.run = self.update_camera
            self.camera_thread.start()
        else:
            print("Selected camera is not available.")

    def stop_camera(self):
        self.camera_active = False
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.quit()
            self.camera_thread.wait()
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        self.clear_display()

    def update_camera(self):
        while self.camera_active and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_image = frame
                self.frame_ready.emit(frame)
            QThread.msleep(16)

    def clear_display(self):
        self.main_window.displayLabel.clear()
        self.main_window.displayLabel.setStyleSheet("background-color: black; border: 2px solid #444444;")

    def __del__(self):
        self.stop_camera()


class DetectionManager(QObject):
    detections_ready = pyqtSignal(list)

    def __init__(self, model, main_window):
        super().__init__()
        self.detection_active = False
        self.model = model
        self.detections = []
        self.main_window = main_window
        self.detection_thread = None

    def toggle_detection(self):
        self.detection_active = not self.detection_active
        if self.detection_active:
            self.main_window.startDetectionButton.setText("Stop Detection")
            self.detection_thread = QThread()
            self.detection_thread.run = self.process_camera_feed
            self.detection_thread.start()
        else:
            self.main_window.startDetectionButton.setText("Start Detection")
            self.stop_detection()

    def stop_detection(self):
        self.detection_active = False
        if self.detection_thread and self.detection_thread.isRunning():
            self.detection_thread.terminate()
            self.detection_thread.wait()

    def process_camera_feed(self):
        while self.detection_active and window.camera_manager.cap and window.camera_manager.cap.isOpened():
            if window.camera_manager.current_image is not None:
                self.detections = self.process_image(window.camera_manager.current_image)
                self.detections_ready.emit(self.detections)
            QThread.msleep(1000)

    def process_image(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        confidence_threshold = window.confidenceSlider.value()
        try:
            result = self.model.predict(image_rgb, confidence=confidence_threshold, overlap=30).json()
            return result['predictions']
        except requests.exceptions.ConnectionError:
            print("Connection Error. Retrying.")
            QThread.sleep(3)
            return self.process_image(image)


class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 20)
        self.cell(0, 5, "Proctor AI", ln=True, align='C')
        self.cell(0, 8, "Generated Report", ln=True, align='C')
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def body(self, proctor, block, date, subject, room, start, end):
        self.set_font("Arial", 'B', 12)
        self.cell(120, 7, f"Name: {proctor}", ln=False)
        self.cell(0, 7, f"Time Generated: {datetime.now().strftime('%H:%M:%S')}", ln=True)
        self.cell(120, 7, f"Exam Date: {date}", ln=False)
        self.cell(0, 7, f"Subject: {subject}", ln=True)
        self.cell(120, 7, f"Block: {block}", ln=False)
        self.cell(0, 7, f"Room: {room}", ln=True)
        self.cell(120, 7, f"Start Time: {start}", ln=False)
        self.cell(0, 7, f"End Time: {end}", ln=True)

    @staticmethod
    def prompt_report_details():
        dialog = QDialog()
        dialog.setWindowTitle("Report Details")
        layout = QVBoxLayout(dialog)

        def create_label_entry(text):
            label = QLabel(text)
            entry = QLineEdit()
            layout.addWidget(label)
            layout.addWidget(entry)
            return entry

        entry_proctor = create_label_entry("Proctor's Name:")
        entry_block = create_label_entry("Block:")
        entry_date = QDateEdit(calendarPopup=True)
        entry_date.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Exam Date:"))
        layout.addWidget(entry_date)
        entry_subject = create_label_entry("Subject:")
        entry_room = create_label_entry("Room:")
        entry_start = QComboBox()
        entry_start.addItems([f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)])
        layout.addWidget(QLabel("Start Time:"))
        layout.addWidget(entry_start)
        entry_end = QComboBox()
        entry_end.addItems([f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)])
        layout.addWidget(QLabel("End Time:"))
        layout.addWidget(entry_end)

        submit_button = QPushButton("Submit")
        layout.addWidget(submit_button)

        def on_submit():
            dialog.accept()

        submit_button.clicked.connect(on_submit)
        dialog.exec_()

        return (entry_proctor.text(), entry_block.text(), entry_date.date().toString("yyyy-MM-dd"),
                entry_subject.text(), entry_room.text(), entry_start.currentText(), entry_end.currentText())

    @staticmethod
    def save_pdf():
        proctor, block, date, subject, room, start, end = PDFReport.prompt_report_details()
        if not all([proctor, block, date, subject, room, start, end]):
            QMessageBox.critical(None, "Error", "All fields must be filled out.")
            return

        db_manager.insert_report_details(proctor, block, date, subject, room, start, end)

        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Report')
        pdf_filename, _ = QFileDialog.getSaveFileName(None, "Save PDF", desktop_path, "PDF files (*.pdf)")
        if not pdf_filename:
            return

        pdf = PDFReport()
        pdf.set_auto_page_break(auto=True, margin=10)
        pdf.add_page()
        pdf.body(proctor, block, date, subject, room, start, end)

        image_count = 0
        x_positions = [10, 110]
        y_positions = [pdf.get_y() + 10, pdf.get_y() + 110]

        for filename in os.listdir("tempcaptures"):
            if filename.endswith(".jpg"):
                if image_count > 0 and image_count % 4 == 0:
                    pdf.add_page()
                    y_positions = [pdf.get_y() + 10, pdf.get_y() + 110]

                image_path = os.path.join("tempcaptures", filename)
                x = x_positions[image_count % 2]
                y = y_positions[(image_count // 2) % 2]
                pdf.image(image_path, x=x, y=y, w=90, h=90)
                image_count += 1

        pdf.output(pdf_filename)
        QMessageBox.information(None, "PDF Saved", f"PDF saved as {pdf_filename}")
        GUIManager.cleanup()


class GUIManager:
    @staticmethod
    def update_status(internet_status_label, database_status_label):
        GUIManager.update_internet_status(internet_status_label)
        GUIManager.update_database_status(database_status_label)

    @staticmethod
    def update_internet_status(internet_status_label):
        internet_status = "Connected" if GUIManager.check_internet_connection() else "Disconnected"
        internet_status_label.setText(f"Internet: {internet_status}")

    @staticmethod
    def update_database_status(database_status_label):
        if db_manager.connection is None or not db_manager.connection.is_connected():
            db_manager.connect()
        database_status = "Connected" if db_manager.connection and db_manager.connection.is_connected() else "Disconnected"
        database_status_label.setText(f"Database: {database_status}")

    @staticmethod
    def check_internet_connection():
        try:
            requests.get("http://www.google.com", timeout=3)
            return True
        except requests.ConnectionError:
            return False

    @staticmethod
    def create_temp_folder():
        if not os.path.exists("tempcaptures"):
            os.makedirs("tempcaptures")

    @staticmethod
    def capture_image(detection, current_image):
        selected_class = window.get_selected_capture_class()
        if detection['class'] != selected_class:
            return

        x_center, y_center = detection['x'], detection['y']
        width, height = int(detection['width'] * 1.5), int(detection['height'] * 1.5)
        x0, y0 = int(x_center - width / 2), int(y_center - height / 2)
        x1, y1 = int(x_center + width / 2), int(y_center + height / 2)

        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(current_image.shape[1], x1)
        y1 = min(current_image.shape[0], y1)

        image = current_image[y0:y1, x0:x1]

        if image.size == 0:
            print(f"Invalid crop: x0={x0}, y0={y0}, x1={x1}, y1={y1}, image_shape={current_image.shape}")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"tempcaptures/cheating_{timestamp}.jpg"

        cv2.imwrite(image_filename, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

    @staticmethod
    def cleanup():
        folder = "tempcaptures"
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
        
        while window.imageLayout.count():
            child = window.imageLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    @staticmethod
    def display_frame(frame, display_label):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        selected_filter = window.filterCombo.currentText()
        for detection in window.detection_manager.detections:
            if selected_filter == "All" or detection['class'] == selected_filter:
                GUIManager.draw_bounding_box(image_rgb, detection)
        GUIManager.update_canvas(image_rgb, display_label)

    @staticmethod
    def draw_bounding_box(image, detection):
        fixed_width = 151
        fixed_height = 151

        x_center, y_center = detection['x'], detection['y']

        x0, y0 = int(x_center - fixed_width / 2), int(y_center - fixed_height / 2)
        x1, y1 = int(x_center + fixed_width / 2), int(y_center + fixed_height / 2)

        class_name = detection['class']
        confidence = detection['confidence']
        color = (0, 255, 0) if class_name == "not_cheating" else (255, 0, 0)

        cv2.rectangle(image, (x0, y0), (x1, y1), color, 1)
        label_text = class_name if window.displayModeCombo.currentText() == "draw_labels" else f"{confidence:.2f}%"
        GUIManager.put_text(image, label_text, x0, y0, color)

    @staticmethod
    def put_text(image, text, x, y, color):
        text_size, baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        text_x, text_y = x, y - text_size[1] - 4
        cv2.rectangle(image, (text_x, text_y), (text_x + text_size[0], text_y + text_size[1] + baseline), color, -1)
        cv2.putText(image, text, (text_x, text_y + text_size[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    @staticmethod
    def update_canvas(image_rgb, display_label):
        height, width = image_rgb.shape[:2]
        bytes_per_line = 3 * width
        q_image = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        display_label.setPixmap(QPixmap.fromImage(q_image))

    @staticmethod
    def display_captures(predictions, captures_layout):
        fixed_width = 150
        fixed_height = 150

        for detection in predictions:
            if detection['class'] == window.get_selected_capture_class():
                GUIManager.capture_image(detection, window.camera_manager.current_image)
                image_label = QLabel()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                image_path = f"tempcaptures/cheating_{timestamp}.jpg"
                pixmap = QPixmap(image_path)
                pixmap = pixmap.scaled(fixed_width, fixed_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
                image_label.setFixedSize(fixed_width, fixed_height)
                image_label.setAlignment(Qt.AlignCenter)
                captures_layout.insertWidget(0, image_label, alignment=Qt.AlignCenter)


if __name__ == "__main__":
    if not os.path.exists("tempcaptures"):
        os.makedirs("tempcaptures")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    
    window.show()
    sys.exit(app.exec_())