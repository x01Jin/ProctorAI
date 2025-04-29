from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QConicalGradient
from frontend.themes.theme_manager import ThemeManager

class AnimatedStateButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._active = False
        self._rotation_angle = 0
        self._animation = QPropertyAnimation(self, b"rotation_angle")
        self._animation.setDuration(2000)
        self._animation.setStartValue(0)
        self._animation.setEndValue(360)
        self._animation.setLoopCount(-1)
        self._animation.setEasingCurve(QEasingCurve.Type.Linear)
        self._border_width = 3
        self._active_gradient_colors = [QColor("#2ecc71"), QColor("#ffffff")]
        self._inactive_color = QColor("#e74c3c")
        self.setAutoFillBackground(True)

    @pyqtProperty(float)
    def rotation_angle(self):
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, angle):
        self._rotation_angle = angle
        self.update()

    def set_active(self, active):
        self._active = active
        if active:
            self._animation.start()
        else:
            self._animation.stop()
            self._rotation_angle = 0
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        border_path = QPainterPath()
        border_path.addRoundedRect(
            self._border_width / 2,
            self._border_width / 2,
            self.width() - self._border_width,
            self.height() - self._border_width,
            4,
            4
        )
        if self._active:
            center_x = self.width() / 2
            center_y = self.height() / 2
            gradient = QConicalGradient(center_x, center_y, -self._rotation_angle)
            gradient.setColorAt(0.0, self._active_gradient_colors[0])
            gradient.setColorAt(0.5, self._active_gradient_colors[1])
            gradient.setColorAt(1.0, self._active_gradient_colors[0])
            pen = QPen()
            pen.setWidth(self._border_width)
            pen.setBrush(gradient)
            painter.setPen(pen)
            painter.drawPath(border_path)
        else:
            pen = QPen(self._inactive_color)
            pen.setWidth(self._border_width)
            painter.setPen(pen)
            painter.drawPath(border_path)

        text_rect = self.rect()
        if not self.isEnabled():
            theme_manager = ThemeManager.instance()
            text_color = QColor(theme_manager.button_disabled_text_color())
        else:
            text_color = self.palette().buttonText().color()
        painter.setPen(QPen(text_color))
        painter.drawText(
            text_rect,
            int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter),
            self.text()
        )
