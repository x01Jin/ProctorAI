from pathlib import Path
import configparser

SETTINGS_FILE = "config.ini"
DEFAULT_SETTINGS = {
    'theme': {'theme': 'dark'},
    'roboflow': {
        'api_key': 'REQUIRED',
        'project': 'REQUIRED',
        'model_version': '1',
        'model_classes': 'REQUIRED'
    },
    'database': {
        'host': 'REQUIRED',
        'user': 'REQUIRED',
        'password': '',
        'database': 'REQUIRED'
    }
}
REQUIRED_SETTINGS = {
    'roboflow': ['api_key', 'project', 'model_classes'],
    'database': ['host', 'user', 'database']
}

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    cls.get_instance = staticmethod(get_instance)
    return cls

@singleton
class SettingsManager:
    def __init__(self):
        self.settings_file = SETTINGS_FILE
        self.config = configparser.ConfigParser()
        self._settings_data = {}
        self._default_settings = DEFAULT_SETTINGS.copy()
        if self.config_exists():
            self._settings_data = self.load_settings()
        else:
            self.create_default_config()

    def config_exists(self):
        return Path(self.settings_file).exists()

    def create_default_config(self):
        settings = self._default_settings.copy()
        for section, values in settings.items():
            if section not in self.config:
                self.config[section] = {}
            for key, value in values.items():
                self.config[section][key] = str(value)
        with open(self.settings_file, 'w') as f:
            self.config.write(f)
        self._settings_data = settings
        return settings

    def load_settings(self):
        settings = self._default_settings.copy()
        self.config.read(self.settings_file)
        for section in self.config.sections():
            settings[section] = dict(self.config[section])
        return settings

    def save_settings(self):
        for section, values in self._settings_data.items():
            if section not in self.config:
                self.config[section] = {}
            for key, value in values.items():
                self.config[section][key] = str(value)
        with open(self.settings_file, 'w') as f:
            self.config.write(f)

    def get_setting(self, category, key=None):
        if key:
            return self._settings_data.get(category, {}).get(key)
        return self._settings_data.get(category)

    def update_setting(self, category, key, value):
        if key is None:
            self._settings_data[category] = value
        else:
            if category not in self._settings_data:
                self._settings_data[category] = {}
            self._settings_data[category][key] = value
        self.save_settings()

    def validate_settings(self):
        for section, fields in REQUIRED_SETTINGS.items():
            section_data = self.get_setting(section)
            for field in fields:
                value = section_data.get(field, '').strip()
                if not value or value == 'REQUIRED':
                    raise ValueError(f"Required setting missing: {section}.{field}")
