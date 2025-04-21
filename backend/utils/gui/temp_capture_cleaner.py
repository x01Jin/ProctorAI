import os
import logging

class TempCaptureCleaner:
    logger = logging.getLogger('report')

    @staticmethod
    def cleanup():
        if not os.path.exists("tempcaptures"):
            return
        for filename in os.listdir("tempcaptures"):
            if filename.endswith(".jpg"):
                file_path = os.path.join("tempcaptures", filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    TempCaptureCleaner.logger.error(f"Error deleting file {file_path}: {e}")
