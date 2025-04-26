from PyQt6.QtWidgets import QMessageBox
import logging
from backend.controllers.report_controller import save_pdf
from ..detectwarn import show_detection_pdf_warning

logger = logging.getLogger("reports")

def generate_pdf(window):
    try:
        if getattr(window.detection_manager, "detection_active", False):
            if show_detection_pdf_warning(window):
                window.detection_manager.toggle_detection(force_stop=True)
                run_pdf_generation(window)
        else:
            run_pdf_generation(window)
    except Exception as e:
        logger.error(f"Error during PDF generation: {str(e)}")

def run_pdf_generation(window):
    def generate_in_background():
        try:
            save_pdf()
            return True
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            return False

    def on_pdf_generation_finished():
        logger.info("PDF generation background task finished.")
        window.report_manager.update_image_list()

    def on_pdf_generation_error(error_info):
        etype, evalue, tb = error_info
        logger.error(f"PDF generation error in worker: {etype.__name__}: {evalue}\n{tb}")
        QMessageBox.critical(window, "PDF Error", f"Failed to generate PDF report: {evalue}")

    logger.info("Starting PDF generation in background...")
    worker_signals = window.thread_pool_manager.run(generate_in_background)
    worker_signals.finished.connect(on_pdf_generation_finished)
    worker_signals.error.connect(on_pdf_generation_error)
