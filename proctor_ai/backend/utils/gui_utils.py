from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import cv2
import os
import shutil
import requests
from proctor_ai.backend.services.database_service import db_manager
from proctor_ai.frontend.components.image_label import ImageLabel

class GUIManager:
    @staticmethod
    def update_status(internet_status_label, database_status_label):
        GUIManager.update_internet_status(internet_status_label)
        GUIManager.update_database_status(database_status_label)

    @staticmethod
    def update_internet_status(internet_status_label):
        internet_status = "Connected" if GUIManager.connection() else "Disconnected"
        internet_status_label.setText(f"Internet: {internet_status}")

    @staticmethod
    def update_database_status(database_status_label):
        if db_manager.connection is None or not db_manager.connection.is_connected():
            db_manager.connect()
        database_status = "Connected" if db_manager.connection and db_manager.connection.is_connected() else "Disconnected"
        database_status_label.setText(f"Database: {database_status}")

    @staticmethod
    def connection():
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
    def cleanup_files():
        folder = "tempcaptures"
        if not os.path.exists(folder):
            return
            
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    @staticmethod
    def cleanup_gui(window):
        if not hasattr(window, 'imageLayout'):
            return
            
        while window.imageLayout.count():
            child = window.imageLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                window.imageLayout.removeWidget(child.widget())
            else:
                window.imageLayout.removeItem(child)

    @staticmethod
    def refresh_captures(captures_layout):
        while captures_layout.count():
            child = captures_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                captures_layout.removeWidget(child.widget())
            else:
                captures_layout.removeItem(child)
        GUIManager.add_new_images_to_layout(set(), captures_layout)

    @staticmethod
    def cleanup(window):
        GUIManager.cleanup_gui(window)
        GUIManager.cleanup_files()
        if hasattr(window, 'imageLayout'):
            GUIManager.refresh_captures(window.imageLayout)

    @staticmethod
    def display_frame(frame, display_label, window):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        selected_filter = window.filterCombo.currentText()
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
        q_image = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        display_label.setPixmap(QPixmap.fromImage(q_image))

    @staticmethod
    def display_captures(predictions, captures_layout, window):
        existing_images = GUIManager.get_existing_images(captures_layout)
        GUIManager.add_new_images_to_layout(existing_images, captures_layout)
        GUIManager.capture_and_add_new_detections(predictions, existing_images, captures_layout, window)

    @staticmethod
    def get_existing_images(captures_layout):
        return {child.widget().image_path for child in (captures_layout.itemAt(i) for i in range(captures_layout.count())) if child.widget()}

    @staticmethod
    def add_new_images_to_layout(existing_images, captures_layout):
        fixed_width = 150
        fixed_height = 150

        for filename in os.listdir("tempcaptures"):
            if filename.endswith(".jpg"):
                image_path = os.path.join("tempcaptures", filename)
                if image_path not in existing_images:
                    GUIManager.add_image_label_to_layout(image_path, captures_layout, fixed_width, fixed_height)

    @staticmethod
    def capture_and_add_new_detections(predictions, existing_images, captures_layout, window):
        for detection in predictions:
            if detection['class'] == window.get_selected_capture_class():
                GUIManager.capture_image(detection, window.camera_manager.current_image, window)
                GUIManager.add_new_images_to_layout(existing_images, captures_layout)

    @staticmethod
    def add_image_label_to_layout(image_path, captures_layout, fixed_width, fixed_height):
        image_label = ImageLabel(image_path)
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(fixed_width, fixed_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image_label.setPixmap(pixmap)
        image_label.setFixedSize(fixed_width, fixed_height)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        captures_layout.insertWidget(0, image_label, alignment=Qt.AlignmentFlag.AlignCenter)
