from PyQt6.QtWidgets import QDialog
from .dialog_builder import DialogBuilder
from .field_validator import FieldValidator
from .details_collector import DetailsCollector

class ReportDialog(QDialog):
    def __init__(self, user_id, proctor_name):
        super().__init__()
        self.user_id = user_id
        self.proctor_name = proctor_name
        self.builder = DialogBuilder(self)
        self.widgets = self.builder.build_widgets()
        self.widgets['proctor'].entry.setText(self.proctor_name)
        self.builder.add_widgets_to_layout(self.widgets)
        self.submit_button = self.builder.setup_submit_button()
        self._setup_validation()
        self.details = None

    def _setup_validation(self):
        self.widgets['proctor'].connect_change_handler(self._validate_fields)
        self.widgets['block'].connect_change_handler(self._validate_fields)
        self.widgets['subject'].connect_change_handler(self._validate_fields)
        self.widgets['room'].connect_change_handler(self._validate_fields)
        self.widgets['num_students'].connect_change_handler(self._validate_fields)
        self.submit_button.clicked.connect(self._on_submit)

    def _validate_fields(self):
        valid = all([
            self.widgets['proctor'].text(),
            self.widgets['block'].has_complete_input(),
            self.widgets['subject'].text(),
            self.widgets['room'].has_complete_input(),
            self.widgets['num_students'].text()
        ])
        self.submit_button.setEnabled(valid)
        self.submit_button.setToolTip("" if valid else "All fields must be filled out")

    def _on_submit(self):
        validator = FieldValidator()
        w = self.widgets

        students_result = validator.validate_students(w['num_students'].text())
        if not students_result:
            self.builder.show_error(students_result.error)
            return

        block_parts = [w['block'].year.text(), w['block'].course.text(), w['block'].number.text()]
        block_result = validator.validate_block(*block_parts)
        if not block_result:
            self.builder.show_error(block_result.error)
            return

        room_result = validator.validate_room(w['room'].get_building(), w['room'].get_number())
        if not room_result:
            self.builder.show_error(room_result.error)
            return

        time_result = validator.validate_time_range(
            w['start_time'].get_time_24h(),
            w['end_time'].get_time_24h()
        )
        if not time_result:
            self.builder.show_error(time_result.error)
            return

        self.details = DetailsCollector.collect_details(self.widgets, self.user_id)
        self.accept()

def prompt_report_details(user_id, proctor_name):
    dialog = ReportDialog(user_id, proctor_name)
    if dialog.exec() and dialog.details:
        return DetailsCollector.unpack_details(dialog.details)
    return None
