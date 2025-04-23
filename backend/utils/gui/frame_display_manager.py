import cv2
import logging
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PyQt6.QtCore import Qt
from frontend.themes.boxcolors import get_box_palette

camera_logger = logging.getLogger('camera')
report_logger = logging.getLogger('report')

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
                draw_bounding_box(image_rgb, detection, window)
        update_canvas(image_rgb, display_label)
    except Exception:
        update_canvas(image_rgb, display_label)

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
        color_index = hash(class_name) % 10
        theme = window.theme_manager.get_current_theme()
        box_color, text_color = get_box_palette(color_index, theme)
        cv2.rectangle(image, (x0, y0), (x1, y1), box_color, 1)
        label_text = class_name if window.detection_controls.display_mode_combo.currentText() == "Draw Labels" else f"{(confidence * 100):.0f}%"
        put_text(image, label_text, x0, y0, box_color, text_color)
    except Exception as e:
        report_logger.error(f"Error drawing bounding box: {e}")

def put_text(image, text, x, y, box_color, text_color):
    try:
        text_size, baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        text_x, text_y = x, y - text_size[1] - 4
        cv2.rectangle(image, (text_x, text_y), (text_x + text_size[0], text_y + text_size[1] + baseline), box_color, -1)
        cv2.putText(image, text, (text_x, text_y + text_size[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
    except Exception as e:
        report_logger.error(f"Error putting text on image: {e}")

class FrameDisplayBuffer:
    _cache = {}
    _last_size = None
    
    @classmethod
    def get_background(cls, width, height):
        size_key = (width, height)
        if size_key != cls._last_size:
            if cls._last_size in cls._cache:
                del cls._cache[cls._last_size]
            bg = QPixmap(width, height)
            bg.fill(Qt.GlobalColor.black)
            cls._cache[size_key] = bg
            cls._last_size = size_key
        return cls._cache[size_key]

def update_canvas(image_rgb, display_label):
    try:
        if image_rgb is None or image_rgb.size == 0:
            camera_logger.error("Invalid image data for canvas update")
            return
            
        label_width = display_label.width()
        label_height = display_label.height()
        
        if label_width <= 0 or label_height <= 0:
            return
            
        if len(image_rgb.shape) != 3 or image_rgb.shape[2] != 3:
            camera_logger.error("Invalid image format")
            return
            
        display_size = (min(label_width, 1280), min(label_height, 720))
        image_rgb = cv2.resize(image_rgb, display_size, interpolation=cv2.INTER_AREA)
        
        bytes_per_line = 3 * image_rgb.shape[1]
        q_image = QImage(image_rgb.data, image_rgb.shape[1], image_rgb.shape[0], 
                        bytes_per_line, QImage.Format.Format_RGB888)
        
        if q_image.isNull():
            camera_logger.error("Failed to create QImage")
            return
            
        bg_pixmap = FrameDisplayBuffer.get_background(label_width, label_height)
        scaled_pixmap = QPixmap.fromImage(q_image).scaled(
            label_width, label_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )
        
        x = (label_width - scaled_pixmap.width()) // 2
        y = (label_height - scaled_pixmap.height()) // 2
        
        painter = QPainter(bg_pixmap)
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()
        
        display_label.setPixmap(bg_pixmap)
    except Exception as e:
        camera_logger.error(f"Error updating canvas: {e}")
