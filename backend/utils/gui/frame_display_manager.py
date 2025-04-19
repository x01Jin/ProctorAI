import cv2
import logging
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PyQt6.QtCore import Qt

camera_logger = logging.getLogger('camera')

class FrameDisplayManager:
    logger = logging.getLogger('report')

    @staticmethod
    def display_frame(frame, display_label, window):
        if frame is None:
            return
        try:
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except cv2.error:
            return
        try:
            selected_filter = window.detection_controls.filter_combo.currentText()
            for detection in window.detection_manager.detections:
                if selected_filter == "All" or detection['class'] == selected_filter:
                    FrameDisplayManager.draw_bounding_box(image_rgb, detection, window)
            FrameDisplayManager.update_canvas(image_rgb, display_label)
        except Exception:
            FrameDisplayManager.update_canvas(image_rgb, display_label)

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
                0: (0, 165, 255),
                1: (255, 0, 128),
                2: (255, 255, 0),
                3: (0, 255, 255),
                4: (203, 192, 255),
                5: (42, 42, 165),
                6: (250, 230, 230),
                7: (208, 224, 64),
                8: (214, 112, 218),
                9: (180, 130, 70),
            }
            color_index = hash(class_name) % 10
            color = CLASS_COLORS[color_index]
            cv2.rectangle(image, (x0, y0), (x1, y1), color, 1)
            label_text = class_name if window.detection_controls.display_mode_combo.currentText() == "Draw Labels" else f"{(confidence * 100):.0f}%"
            FrameDisplayManager.put_text(image, label_text, x0, y0, color)
        except Exception as e:
            FrameDisplayManager.logger.error(f"Error drawing bounding box: {e}")

    @staticmethod
    def put_text(image, text, x, y, color):
        try:
            text_size, baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            text_x, text_y = x, y - text_size[1] - 4
            cv2.rectangle(image, (text_x, text_y), (text_x + text_size[0], text_y + text_size[1] + baseline), color, -1)
            negative_color = tuple(255 - c for c in color)
            cv2.putText(image, text, (text_x, text_y + text_size[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, negative_color, 1)
        except Exception as e:
            FrameDisplayManager.logger.error(f"Error putting text on image: {e}")

    @staticmethod
    def update_canvas(image_rgb, display_label):
        try:
            if image_rgb is None or image_rgb.size == 0:
                camera_logger.error("Invalid image data for canvas update")
                return
            bytes_per_line = 3 * image_rgb.shape[1]
            q_image = QImage(image_rgb.data, image_rgb.shape[1], image_rgb.shape[0], bytes_per_line, QImage.Format.Format_RGB888)
            if q_image.isNull():
                camera_logger.error("Failed to create QImage from frame data")
                return
            pixmap = QPixmap.fromImage(q_image)
            label_width = display_label.width()
            label_height = display_label.height()
            scaled_pixmap = pixmap.scaled(
                label_width,
                label_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (label_width - scaled_pixmap.width()) // 2
            y = (label_height - scaled_pixmap.height()) // 2
            bg_pixmap = QPixmap(label_width, label_height)
            bg_pixmap.fill(Qt.GlobalColor.black)
            painter = QPainter(bg_pixmap)
            painter.drawPixmap(x, y, scaled_pixmap)
            painter.end()
            display_label.setPixmap(bg_pixmap)
        except Exception as e:
            camera_logger.error(f"Error updating canvas: {e}")
