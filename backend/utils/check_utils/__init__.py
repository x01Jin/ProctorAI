from .check_config import check_config
from .check_internet import check_internet
from .check_roboflow import check_roboflow
from .check_dbc import check_database
from PyQt6.QtCore import QTimer

def run_checks(log_display, on_complete):
    def after_config(config_ok):
        if config_ok:
            check_internet(log_display, after_internet)

    def after_internet(internet_ok):
        if internet_ok:
            check_roboflow(log_display, after_roboflow)

    def after_roboflow(roboflow_ok):
        if roboflow_ok:
            check_database(log_display, after_database)

    def after_database(database_ok):
        log_display.log("All checks complete, logging in...", "info")
        QTimer.singleShot(500, lambda: on_complete(database_ok))

    check_config(log_display, after_config)
