from PyQt6.QtCore import QThread

def start_qthread(qthread: QThread):
    if qthread and not qthread.isRunning():
        qthread.start()

def stop_qthread(qthread: QThread):
    if qthread and qthread.isRunning():
        if hasattr(qthread, "stop"):
            qthread.stop()
        qthread.wait()
