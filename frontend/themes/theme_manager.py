from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QObject

class ThemeManager(QObject):
    theme_changed = pyqtSignal()

    _instance = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_theme = None
        self._palette = None
        theme = None
        if self.parent and hasattr(self.parent, "settings"):
            theme = self.parent.settings.get_setting("theme", "theme")
        self.apply_theme(theme if theme else "dark")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def set_parent(self, parent):
        self.parent = parent

    def apply_theme(self, theme_name):
        if theme_name == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
        self.current_theme = theme_name
        self.theme_changed.emit()

    def apply_dark_theme(self):
        palette = {
            "background": "#353535",
            "text": "#ffffff"
        }
        self._palette = palette
        if self.parent:
            qt_palette = QPalette()
            qt_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            qt_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            qt_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
            qt_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            qt_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            qt_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            qt_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            qt_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            qt_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            qt_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            qt_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
            self.parent.setPalette(qt_palette)

    def apply_light_theme(self):
        palette = {
            "background": "#ffffff",
            "text": "#000000"
        }
        self._palette = palette
        if self.parent:
            qt_palette = QPalette()
            qt_palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
            qt_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
            qt_palette.setColor(QPalette.ColorRole.Base, QColor(245, 245, 245))
            qt_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(255, 255, 255))
            qt_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
            qt_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
            qt_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
            qt_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
            qt_palette.setColor(QPalette.ColorRole.Button, QColor(255, 255, 255))
            qt_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            qt_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
            self.parent.setPalette(qt_palette)

    def get_current_theme(self):
        return self.current_theme

    def current_palette(self):
        return self._palette if self._palette else {"background": "#353535", "text": "#ffffff"}
