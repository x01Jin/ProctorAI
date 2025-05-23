from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

def show_detection_pdf_warning(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle('Detection is still running')
    layout = QVBoxLayout(dialog)
    label = QLabel(
        'Detection is still running:\n'
        '• Detection should be stopped when attempting to generate a report\n'
        '• Choosing the Continue option will automatically stop the detection\n'
        '• Choosing the Cancel option will cancel the report generation attempt and continue detection'
    )
    label.setWordWrap(True)
    layout.addWidget(label)
    button_layout = QHBoxLayout()
    continue_btn = QPushButton('Continue')
    cancel_btn = QPushButton('Cancel')
    button_layout.addWidget(continue_btn)
    button_layout.addWidget(cancel_btn)
    layout.addLayout(button_layout)

    result = {'continue': False}

    def on_continue():
        result['continue'] = True
        dialog.accept()

    def on_cancel():
        dialog.reject()

    continue_btn.clicked.connect(on_continue)
    cancel_btn.clicked.connect(on_cancel)

    dialog.setLayout(layout)
    dialog.setModal(True)
    dialog.exec()
    return result['continue']

def show_settings_interrupt_warning(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle('Camera/Detection is Active')
    layout = QVBoxLayout(dialog)
    label = QLabel(
        'The camera/detection is currently active:\n'
        '• Choosing Continue will open settings but changing/modifying settings and saving or just saving will interrupt detection process.\n'
        '• If you opened settings but decided to not change anything at all just exit/cancel settings without saving.\n'
        '• Choosing Cancel will keep detection running and not open settings.'
    )
    label.setWordWrap(True)
    layout.addWidget(label)
    button_layout = QHBoxLayout()
    continue_btn = QPushButton('Continue')
    cancel_btn = QPushButton('Cancel')
    button_layout.addWidget(continue_btn)
    button_layout.addWidget(cancel_btn)
    layout.addLayout(button_layout)

    result = {'continue': False}

    def on_continue():
        result['continue'] = True
        dialog.accept()

    def on_cancel():
        dialog.reject()

    continue_btn.clicked.connect(on_continue)
    cancel_btn.clicked.connect(on_cancel)

    dialog.setLayout(layout)
    dialog.setModal(True)
    dialog.exec()
    return result['continue']
