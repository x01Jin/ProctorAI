import cv2
import random
import string
import logging
from PIL import Image, ImageDraw, ImageFont
import time
import os
from backend.utils.deduplication_utils import DetectionDeduplicator

class ImageCaptureManager:
    logger = logging.getLogger('report')
    WATERMARK_FONT_SIZE = 12
    WATERMARK_MARGIN = 4
    WINDOWS_FONT_PATH = "C:/Windows/Fonts/times.ttf"
    
    @staticmethod
    def _get_font():
        return ImageFont.truetype(ImageCaptureManager.WINDOWS_FONT_PATH, ImageCaptureManager.WATERMARK_FONT_SIZE) if os.path.exists(ImageCaptureManager.WINDOWS_FONT_PATH) else ImageFont.load_default()
    
    @staticmethod
    def _cv2_to_pil(image):
        return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    @staticmethod
    def _add_watermark(pil_image):
        draw = ImageDraw.Draw(pil_image)
        font = ImageCaptureManager._get_font()
        current_time = time.strftime('%I:%M %p').lstrip('0')
        watermark_text = f"Time captured: {current_time}"
        
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_height = text_bbox[3] - text_bbox[1]
        
        x, y = ImageCaptureManager.WATERMARK_MARGIN, pil_image.height - text_height - ImageCaptureManager.WATERMARK_MARGIN
        
        for bx, by in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]:
            draw.text((bx, by), watermark_text, fill='black', font=font)
        draw.text((x, y), watermark_text, fill='white', font=font)
        
        return pil_image
    
    @staticmethod
    def capture_image(detection, current_image, window):
        if detection['class'] != window.get_selected_capture_class():
            return
            
        if DetectionDeduplicator._in_deadzone(detection):
            ImageCaptureManager.logger.info(f"Skipped capture: detection in deadzone {detection}")
            return
        
        x_center, y_center = detection['x'], detection['y']
        display_width = window.camera_display.display_label.width()
        capture_size = int(display_width * 0.20 * 1.2)
        
        x0 = max(0, int(x_center - capture_size / 2))
        y0 = max(0, int(y_center - capture_size / 2))
        x1 = min(current_image.shape[1], int(x_center + capture_size / 2))
        y1 = min(current_image.shape[0], int(y_center + capture_size / 2))
        
        cropped_image = current_image[y0:y1, x0:x1]
        if cropped_image.size == 0:
            ImageCaptureManager.logger.error(f"Invalid crop: {x0},{y0},{x1},{y1}, shape={current_image.shape}")
            return

        pil_image = ImageCaptureManager._cv2_to_pil(cropped_image)
        pil_image = ImageCaptureManager._add_watermark(pil_image)
        
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        image_filename = f"tempcaptures/untagged({random_id}).jpg"
        pil_image.save(image_filename, quality=100, subsampling=0)
        
        DetectionDeduplicator._add_deadzone(detection, time.time())
