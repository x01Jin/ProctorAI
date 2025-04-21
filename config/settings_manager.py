from pathlib import Path
import configparser

SETTINGS_FILE = "config.ini"
REQUIRED_SETTINGS = {
    'roboflow': ['api_key', 'project', 'model_classes'],
    'database': ['host', 'user', 'database']
}

_settings_data = {}

def config_exists(settings_file=SETTINGS_FILE):
    return Path(settings_file).exists()


def load_settings(settings_file=SETTINGS_FILE):
    config = configparser.ConfigParser()
    config.read(settings_file)
    settings = {}
    for section in config.sections():
        settings[section] = dict(config[section])
    global _settings_data
    _settings_data = settings
    return settings

def save_settings(settings_file=SETTINGS_FILE):
    config = configparser.ConfigParser()
    for section, values in _settings_data.items():
        if section not in config:
            config[section] = {}
        for key, value in values.items():
            config[section][key] = str(value)
    with open(settings_file, 'w') as f:
        config.write(f)

def get_setting(category, key=None):
    if key:
        return _settings_data.get(category, {}).get(key)
    return _settings_data.get(category)

def update_setting(category, key, value):
    if key is None:
        _settings_data[category] = value
    else:
        if category not in _settings_data:
            _settings_data[category] = {}
        _settings_data[category][key] = value
    save_settings()

def validate_settings():
    for section, fields in REQUIRED_SETTINGS.items():
        section_data = get_setting(section)
        for field in fields:
            value = section_data.get(field, '').strip()
            if not value or value == 'REQUIRED':
                raise ValueError(f"Required setting missing: {section}.{field}")
