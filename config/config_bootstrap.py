from config.settings_manager import config_exists, load_settings, ensure_config_directory, CONFIG_FILE
import configparser

DEFAULT_SETTINGS = {
    'theme': {'theme': 'dark'}
}

def create_default_config():
    try:
        ensure_config_directory()
        config = configparser.ConfigParser()
        settings = DEFAULT_SETTINGS.copy()
        for section, values in settings.items():
            if section not in config:
                config[section] = {}
            for key, value in values.items():
                config[section][key] = str(value)
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
        return True
    except Exception:
        return False

def ensure_config(parent, log_display):
    if config_exists():
        try:
            load_settings()
            return True
        except Exception:
            return False
    
    log_display.log("No configuration file found, Attempting to create the configuration file with default values...", "warning")
    
    if not create_default_config():
        return False
        
    try:
        load_settings()
        log_display.log("Configuration file created...", "success")
        return True
    except Exception:
        return False
