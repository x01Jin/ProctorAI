from pathlib import Path
import configparser
import os
import shutil

APP_NAME = "ProctorAI"
CONFIG_DIR = Path(os.getenv('APPDATA')) / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.ini"

def ensure_config_directory():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
REQUIRED_SETTINGS = {
    'roboflow': ['api_key', 'project', 'model_classes'],
    'database': ['host', 'user', 'database']
}

_settings_data = {}

def config_exists():
    old_config = Path("config.ini")
    if old_config.exists():
        ensure_config_directory()
        shutil.copy2(old_config, CONFIG_FILE)
        old_config.unlink()
    return CONFIG_FILE.exists()


def load_settings():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    settings = {}
    for section in config.sections():
        settings[section] = dict(config[section])
    global _settings_data
    _settings_data = settings
    return settings

def save_settings():
    ensure_config_directory()
    config = configparser.ConfigParser()
    for section, values in _settings_data.items():
        if section not in config:
            config[section] = {}
        for key, value in values.items():
            config[section][key] = str(value)
    with open(CONFIG_FILE, 'w') as f:
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
