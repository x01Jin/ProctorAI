import os
import logging
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter
from frontend.components.image_label import ImageLabel

class ImageLabelManager:
    logger = logging.getLogger('report')

    @staticmethod
    def add_image_label_to_layout(image_path, captures_layout, fixed_size=150):
        if not os.path.exists(image_path):
            ImageLabelManager.logger.error(f"Image file not found: {image_path}")
            return
        container = QFrame()
        container.image_path = image_path
        container.setStyleSheet(
            "QFrame {background-color: #1e1e1e; padding: 8px; border: 1px solid #333333; border-radius: 4px; margin: 4px;}"
        )
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
            ImageLabelManager.logger.error(f"Failed to load image: {image_path}")
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

    @staticmethod
    def remove_image_from_layout(image_path, captures_layout):
        for i in range(captures_layout.count()):
            item = captures_layout.itemAt(i)
            if not item:
                continue
            container = item.widget()
            if not container:
                captures_layout.takeAt(i)
                continue
            if hasattr(container, 'image_path') and container.image_path == image_path:
                container.deleteLater()
                captures_layout.takeAt(i)
                if captures_layout.parentWidget():
                    captures_layout.parentWidget().update()
                break
