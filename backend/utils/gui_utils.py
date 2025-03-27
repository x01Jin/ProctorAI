from PyQt6.QtGui import QPixmap, QImage, QPainter
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
import cv2
import os
import logging
import requests
from backend.services.application_state import ApplicationState
from frontend.components.image_label import ImageLabel

class GUIManager:
    logger = logging.getLogger('report')

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
        try:
            selected_class = window.get_selected_capture_class()
            if detection['class'] != selected_class:
                return

            x_center, y_center = detection['x'], detection['y']
            display_width = window.camera_display.display_label.width()
            box_size = int(display_width * 0.20)
            capture_size = int(box_size * 1.2)
            
            x0 = int(x_center - capture_size / 2)
            y0 = int(y_center - capture_size / 2)
            x1 = int(x_center + capture_size / 2)
            y1 = int(y_center + capture_size / 2)

            x0 = max(0, x0)
            y0 = max(0, y0)
            x1 = min(current_image.shape[1], x1)
            y1 = min(current_image.shape[0], y1)

            image = current_image[y0:y1, x0:x1]

            if image.size == 0:
                GUIManager.logger.error(f"Invalid crop: x0={x0}, y0={y0}, x1={x1}, y1={y1}, image_shape={current_image.shape}")
                return

            existing_files = os.listdir("tempcaptures")
            image_number = 1
            while f"untagged({image_number}).jpg" in existing_files:
                image_number += 1
            image_filename = f"tempcaptures/untagged({image_number}).jpg"

            cv2.imwrite(image_filename, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            GUIManager.logger.info(f"Captured image saved to: {image_filename}")

        except Exception as e:
            GUIManager.logger.error(f"Error capturing image: {e}")

    @staticmethod
    def display_frame(frame, display_label, window):
        try:
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            selected_filter = window.detection_controls.filter_combo.currentText()
            for detection in window.detection_manager.detections:
                if selected_filter == "All" or detection['class'] == selected_filter:
                    GUIManager.draw_bounding_box(image_rgb, detection, window)
            GUIManager.update_canvas(image_rgb, display_label)
        except Exception as e:
            GUIManager.logger.error(f"Error displaying frame: {e}")

    @staticmethod
    def draw_bounding_box(image, detection, window):
        try:
            x_center, y_center = detection['x'], detection['y']
            display_width = window.camera_display.display_label.width()
            box_size = int(display_width * 0.20)

            x0 = int(x_center - box_size / 2)
            y0 = int(y_center - box_size / 2)
            x1 = int(x_center + box_size / 2)
            y1 = int(y_center + box_size / 2)

            class_name = detection['class']
            confidence = detection['confidence']
            
            CLASS_COLORS = {
                0: (0, 165, 255),   # Orange
                1: (255, 0, 128),   # Purple
                2: (255, 255, 0),   # Cyan
                3: (0, 255, 255),   # Yellow
                4: (203, 192, 255), # Pink
                5: (42, 42, 165),   # Brown
                6: (250, 230, 230), # Lavender
                7: (208, 224, 64),  # Turquoise
                8: (214, 112, 218), # Orchid
                9: (180, 130, 70),  # Steel Blue
            }
            
            color_index = hash(class_name) % 10
            color = CLASS_COLORS[color_index]

            cv2.rectangle(image, (x0, y0), (x1, y1), color, 1)
            label_text = class_name if window.detection_controls.display_mode_combo.currentText() == "draw_labels" else f"{(confidence * 100):.0f}%"
            GUIManager.put_text(image, label_text, x0, y0, color)
        except Exception as e:
            GUIManager.logger.error(f"Error drawing bounding box: {e}")

    @staticmethod
    def put_text(image, text, x, y, color):
        try:
            text_size, baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            text_x, text_y = x, y - text_size[1] - 4
            cv2.rectangle(image, (text_x, text_y), (text_x + text_size[0], text_y + text_size[1] + baseline), color, -1)
            cv2.putText(image, text, (text_x, text_y + text_size[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        except Exception as e:
            GUIManager.logger.error(f"Error putting text on image: {e}")

    @staticmethod
    def update_canvas(image_rgb, display_label):
        try:
            height, width = image_rgb.shape[:2]
            bytes_per_line = 3 * width
            q_image = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            # Calculate scaled size maintaining aspect ratio
            label_width = display_label.width()
            label_height = display_label.height()
            
            scaled_pixmap = pixmap.scaled(
                label_width,
                label_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Center the scaled pixmap in the label
            x = (label_width - scaled_pixmap.width()) // 2
            y = (label_height - scaled_pixmap.height()) // 2
            
            # Create a black background pixmap
            bg_pixmap = QPixmap(label_width, label_height)
            bg_pixmap.fill(Qt.GlobalColor.black)
            
            # Paint the scaled image onto the background
            painter = QPainter(bg_pixmap)
            painter.drawPixmap(x, y, scaled_pixmap)
            painter.end()
            
            display_label.setPixmap(bg_pixmap)
        except Exception as e:
            GUIManager.logger.error(f"Error updating canvas: {e}")

    @staticmethod
    def add_image_label_to_layout(image_path, captures_layout, fixed_size=150):
        try:
            if not os.path.exists(image_path):
                GUIManager.logger.error(f"Image file not found: {image_path}")
                return

            container = QFrame()
            container.image_path = image_path
            container.setStyleSheet("""
                QFrame {
                    background-color: #1e1e1e;
                    padding: 8px;
                    border: 1px solid #333333;
                    border-radius: 4px;
                    margin: 4px;
                }
            """)
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(5)
            
            _, filename = os.path.split(image_path)
            name, _ = os.path.splitext(filename)
            filename_label = QLabel(name)
            filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            filename_label.setStyleSheet("QLabel { color: #ffffff; }")
            filename_label.setWordWrap(False)
            
            image_label = ImageLabel(image_path, filename_label=filename_label)
            canvas = QPixmap(fixed_size, fixed_size)
            canvas.fill(Qt.GlobalColor.black)
            
            original = QPixmap(image_path)
            if original.isNull():
                GUIManager.logger.error(f"Failed to load image: {image_path}")
                return

            scaled = original.scaled(fixed_size, fixed_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
            painter = QPainter(canvas)
            x = (fixed_size - scaled.width()) // 2
            y = (fixed_size - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.end()
            
            image_label.setPixmap(canvas)
            image_label.setFixedSize(fixed_size, fixed_size)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            container_layout.addWidget(image_label)
            container_layout.addWidget(filename_label)
            
            metrics = filename_label.fontMetrics()
            text_width = metrics.horizontalAdvance(name)
            max_width = captures_layout.parentWidget().width() * 0.8
            if text_width > max_width:
                elided_text = metrics.elidedText(name, Qt.TextElideMode.ElideRight, int(max_width))
                filename_label.setText(elided_text)
            filename_label.adjustSize()
            
            captures_layout.insertWidget(0, container, alignment=Qt.AlignmentFlag.AlignCenter)
            
            GUIManager.logger.info(f"Added image to layout: {image_path}")
        except Exception as e:
            GUIManager.logger.error(f"Error adding image label to layout: {e}")

    @staticmethod
    def remove_image_from_layout(image_path, captures_layout):
        try:
            for i in range(captures_layout.count()):
                container = captures_layout.itemAt(i).widget()
                if container and hasattr(container, 'image_path') and container.image_path == image_path:
                    container.deleteLater()
                    captures_layout.takeAt(i)
                    GUIManager.logger.info(f"Removed image container from layout: {image_path}")
                    break
        except Exception as e:
            GUIManager.logger.error(f"Error removing image from layout: {e}")
    
    @staticmethod
    def cleanup():
        try:
            if not os.path.exists("tempcaptures"):
                return
                
            for filename in os.listdir("tempcaptures"):
                if filename.endswith(".jpg"):
                    file_path = os.path.join("tempcaptures", filename)
                    try:
                        os.remove(file_path)
                        GUIManager.logger.info(f"Cleaned up file: {file_path}")
                    except Exception as e:
                        GUIManager.logger.error(f"Error deleting file {file_path}: {e}")
        except Exception as e:
            GUIManager.logger.error(f"Error in cleanup: {e}")
