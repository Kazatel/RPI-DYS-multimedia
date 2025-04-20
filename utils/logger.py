import logging
import os

class Logger:
    def __init__(self, log_dir=None, console_level=logging.DEBUG, file_level=logging.DEBUG):
        # Avoid circular import by importing config locally here
        import config  # Local import to prevent circular import

        self.log_dir = log_dir if log_dir else config.LOG_DIR
        self.console_level = console_level
        self.file_level = file_level

        # ✅ Prevent adding handlers more than once
        self.logger = logging.getLogger("app_logger")
        self.logger.setLevel(logging.DEBUG)

        if self.logger.hasHandlers():
            return

        # Ensure log directory exists
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        log_file = os.path.join(self.log_dir, "rpi_dys_multimedia.log")
        self.log_file_path = log_file

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(self.file_level)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.console_level)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)

        # Add handlers once
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def tail_note(self):
        self.info(
            f"📡 You can monitor progress in another terminal with:\n"
            f"    tail -f {self.log_file_path}"
        )

    def get_log_file_path(self):
        return self.log_file_path

    def log_only_no_indicator(self, message):
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.acquire()
                try:
                    handler.stream.write(message + '\n')
                    handler.flush()
                finally:
                    handler.release()

# Singleton pattern to access logger instance globally
logger_instance = Logger()

def get_logger():
    return logger_instance
