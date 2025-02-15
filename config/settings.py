from .settings_manager import SettingsManager
from .settings_dialog import SettingsDialog

# For backward compatibility
Settings = SettingsManager

def show_settings_dialog(parent=None):
    """
    Show the settings dialog and return True if settings were saved successfully.
    """
    dialog = SettingsDialog(parent)
    result = dialog.exec()
    return result == SettingsDialog.Accepted
