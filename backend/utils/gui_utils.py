from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import cv2
import os
import requests
from backend.services.application_state import ApplicationState
from frontend.components.image_label import ImageLabel

class GUIManager:
    @staticmethod
    def update_status(internet_status_label, database_status_label):
        internet_status = GUIManager.check_internet_status()
        database_status = GUIManager.check_database_status()
        
        app_state = ApplicationState.get_instance()
        app_state.update_connection_status(internet=internet_status, database=database_status)
        
        internet_status_label.setText(f"Internet: {'Connected' if internet_status else 'Disconnected'}")
        database_status_label.setText(f"Database: {'Connected' if database_status else 'Disconnected'}")

    @staticmethod
    def check_internet_status():
        try:
            requests.get("http://google.com", timeout=1)
            return True
        except requests.exceptions.RequestException:
            return False

    @staticmethod
    def check_database_status():
        app_state = ApplicationState.get_instance()
        if not app_state.database:
            return False
        return app_state.database.test_connection()

    @staticmethod
    def capture_image(detection, current_image, window):
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

        existing_files = os.listdir("tempcaptures")
        image_number = 1
        while f"untagged({image_number}).jpg" in existing_files:
            image_number += 1
        image_filename = f"tempcaptures/untagged({image_number}).jpg"

        cv2.imwrite(image_filename, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

    @staticmethod
    def display_frame(frame, display_label, window):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        selected_filter = window.detection_controls.filter_combo.currentText()
        for detection in window.detection_manager.detections:
            if selected_filter == "All" or detection['class'] == selected_filter:
                GUIManager.draw_bounding_box(image_rgb, detection, window)
        GUIManager.update_canvas(image_rgb, display_label)

    @staticmethod
    def draw_bounding_box(image, detection, window):
        x_center, y_center = detection['x'], detection['y']
        width, height = detection['width'], detection['height']

        x0, y0 = int(x_center - width / 2), int(y_center - height / 2)
        x1, y1 = int(x_center + width / 2), int(y_center + height / 2)

        class_name = detection['class']
        confidence = detection['confidence']
        color = (0, 255, 0) if class_name == "not_cheating" else (255, 0, 0)

        cv2.rectangle(image, (x0, y0), (x1, y1), color, 1)
        label_text = class_name if window.detection_controls.display_mode_combo.currentText() == "draw_labels" else f"{(confidence * 100):.0f}%"
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
        q_image = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        display_label.setPixmap(QPixmap.fromImage(q_image))

    @staticmethod
    def add_image_label_to_layout(image_path, captures_layout, fixed_width=150, fixed_height=150):
        image_label = ImageLabel(image_path)
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(fixed_width, fixed_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image_label.setPixmap(pixmap)
        image_label.setFixedSize(fixed_width, fixed_height)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        captures_layout.insertWidget(0, image_label, alignment=Qt.AlignmentFlag.AlignCenter)

    @staticmethod
    def remove_image_from_layout(image_path, captures_layout):
        for i in range(captures_layout.count()):
            widget = captures_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'image_path') and widget.image_path == image_path:
                widget.deleteLater()
                captures_layout.takeAt(i)
                break
    
    @staticmethod
    def cleanup():
        if not os.path.exists("tempcaptures"):
            return
            
        for filename in os.listdir("tempcaptures"):
            if filename.endswith(".jpg"):
                file_path = os.path.join("tempcaptures", filename)
                try:
                    os.remove(file_path)
                except OSError:
                    pass
