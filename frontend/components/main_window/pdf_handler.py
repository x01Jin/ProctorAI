from PyQt6.QtWidgets import QMessageBox
import logging
from backend.controllers.report_controller import get_report_details, save_pdf_with_details
from ..detectwarn import show_detection_pdf_warning

logger = logging.getLogger("reports")

def generate_pdf(window):
    try:
        if getattr(window.detection_manager, "detection_active", False):
            if not show_detection_pdf_warning(window):
                return
            window.detection_manager.toggle_detection(force_stop=True)
        details = get_report_details()
        if not details:
            return
        def worker():
            return save_pdf_with_details(details)
        def on_finished():
            window.report_manager.update_image_list()
        def on_result(success):
            if success:
                QMessageBox.information(window, "PDF Saved", "PDF report saved successfully.")
            else:
                QMessageBox.critical(window, "PDF Error", "Failed to save PDF report.")
        def on_error(error_info):
            etype, evalue, tb = error_info
            logger.error(f"PDF generation error: {etype.__name__}: {evalue}\n{tb}")
            QMessageBox.critical(window, "PDF Error", f"Failed to generate PDF report: {evalue}")
        signals = window.thread_pool_manager.run(worker)
        signals.result.connect(on_result)
        signals.finished.connect(on_finished)
        signals.error.connect(on_error)
    except Exception as e:
        logger.error(f"Error during PDF generation: {str(e)}")
