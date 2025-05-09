import os
import logging
from backend.services.application_state import ApplicationState
from backend.utils.gui.temp_capture_cleaner import TempCaptureCleaner
from backend.utils.pdf_template import PDFReport, REPORT_DIR_NAME
from backend.utils.report import prompt_report_details

logger = logging.getLogger("report")

def format_display_name(filename):
    name_without_extension = os.path.splitext(filename)[0]
    display_name = name_without_extension.replace('_', ' ')
    return display_name

def get_report_details(user_id, proctor_name):
    return prompt_report_details(user_id, proctor_name)

def save_pdf_with_details(details):
    if not details:
        return False
    user_id, proctor, block, date, subject, room, start, end, num_students = details
    try:
        app_state = ApplicationState.get_instance()
        db = app_state.database
        if db:
            db.insert_report_details(
                app_state.settings, user_id, block, date, subject, room, start, end, num_students
            )
            logger.info("Inserted report details into database for block=%s, subject=%s, date=%s", block, subject, date)
        else:
            logger.error("Database connection not initialized")
            return False
        desktop_path = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop")
        report_dir = os.path.join(desktop_path, REPORT_DIR_NAME)
        os.makedirs(report_dir, exist_ok=True)
        pdf_filename = os.path.join(report_dir, f"{block}_{subject}_{date}.pdf")
        pdf = PDFReport()
        pdf.set_auto_page_break(auto=True, margin=10)
        pdf.add_page()
        pdf.body(proctor, block, date, subject, room, start, end, num_students)
        image_count = 0
        x_positions = [10, 110]
        y_positions = [pdf.get_y() + 10, pdf.get_y() + 110]
        if not os.path.exists("tempcaptures"):
            return False
        captures = [f for f in os.listdir("tempcaptures") if f.endswith(".jpg")]
        for filename in captures:
            if image_count > 0 and image_count % 4 == 0:
                pdf.add_page()
                y_positions = [pdf.get_y() + 10, pdf.get_y() + 110]
            image_path = os.path.join("tempcaptures", filename)
            x = x_positions[image_count % 2]
            y = y_positions[(image_count // 2) % 2]
            pdf.image(image_path, x=x, y=y, w=90, h=90)
            pdf.set_font("Arial", size=8)
            pdf.set_xy(x, y - 5)
            display_name = format_display_name(filename)
            pdf.cell(90, 5, display_name, 0, 0, "C")
            image_count += 1
        pdf.output(pdf_filename)
        logger.info("PDF report saved: %s", pdf_filename)
        TempCaptureCleaner.cleanup()
        return True
    except Exception as e:
        logger.error("Failed to save PDF report: %s", str(e))
        return False
