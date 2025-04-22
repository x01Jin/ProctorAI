from PyQt6.QtCore import QTimer
import subprocess
import platform

def check_internet(log_display, on_complete, retry_count=3, attempt=0):
    log_display.log("Checking internet connection...")
    def try_ping():
        try:
            command = ["ping", "-n" if platform.system().lower()=="windows" else "-c", "1", "8.8.8.8"]
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            log_display.log("Internet connection established", "success")
            QTimer.singleShot(100, lambda: on_complete(True))
        except subprocess.CalledProcessError:
            if attempt < retry_count - 1:
                log_display.log(f"Internet connection failed, retrying... ({attempt + 1}/{retry_count})", "warning")
                QTimer.singleShot(1000, lambda: check_internet(log_display, on_complete, retry_count, attempt + 1))
            else:
                log_display.log("Internet connection failed after 3 attempts", "error")
                log_display.log("Some features may be limited without internet connection", "warning")
                QTimer.singleShot(100, lambda: on_complete(False))
    QTimer.singleShot(1000, try_ping)
