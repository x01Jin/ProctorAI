import cv2
import random
import string
import logging

class ImageCaptureManager:
    logger = logging.getLogger('report')

    @staticmethod
    def capture_image(detection, current_image, window):
        selected_class = window.get_selected_capture_class()
        if detection['class'] != selected_class:
            return
        from backend.utils.deduplication_utils import DetectionDeduplicator
        if DetectionDeduplicator._in_deadzone(detection):
            ImageCaptureManager.logger.info(f"Skipped capture: detection in deadzone {detection}")
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
            ImageCaptureManager.logger.error(f"Invalid crop: x0={x0}, y0={y0}, x1={x1}, y1={y1}, image_shape={current_image.shape}")
            return
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        image_filename = f"tempcaptures/untagged({random_id}).jpg"
        cv2.imwrite(image_filename, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        from backend.utils.deduplication_utils import DetectionDeduplicator
        import time
        DetectionDeduplicator._add_deadzone(detection, time.time())
