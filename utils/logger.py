import logging
import os
import sys
import traceback
from datetime import datetime
from contextlib import contextmanager

class Logger:
    def __init__(self, log_dir=None, console_level=logging.INFO, file_level=logging.DEBUG):
        # Avoid circular import by importing config locally here
        import config  # Local import to prevent circular import

        self.log_dir = log_dir if log_dir else config.LOG_DIR
        self.console_level = console_level
        self.file_level = file_level
        self.section_level = 0  # For tracking nested log sections

        # ✅ Prevent adding handlers more than once
        self.logger = logging.getLogger("rpi_dys_logger")
        self.logger.setLevel(logging.DEBUG)

        if self.logger.hasHandlers():
            return

        self._setup_handlers()

    def _setup_handlers(self):
        """Set up logging handlers with proper formatting"""
        # Ensure log directory exists
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"rpi_dys_{timestamp}.log")
        self.log_file_path = log_file

        # Create a symlink to the latest log
        latest_link = os.path.join(self.log_dir, "rpi_dys_latest.log")
        if os.path.exists(latest_link):
            try:
                os.remove(latest_link)
            except:
                pass
        try:
            os.symlink(log_file, latest_link)
        except:
            pass

        # File handler with detailed formatting
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(self.file_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)

        # Console handler with simpler formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.console_level)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)

        # Add handlers
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
        """Log a message to file only without any formatting"""
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.acquire()
                try:
                    handler.stream.write(message + '\n')
                    handler.flush()
                finally:
                    handler.release()

    @contextmanager
    def log_section(self, title, level=logging.INFO):
        """Context manager for logging sections with clear boundaries"""
        self.section_level += 1
        indent = "  " * (self.section_level - 1)
        separator = "=" * (50 - len(indent))

        self.logger.log(level, f"\n{indent}{separator}")
        self.logger.log(level, f"{indent}STARTING: {title}")
        self.logger.log(level, f"{indent}{separator}")

        try:
            yield
        except Exception as e:
            self.error(f"{indent}ERROR in {title}: {str(e)}")
            self.debug(f"Exception details:\n{traceback.format_exc()}")
            raise
        finally:
            self.logger.log(level, f"\n{indent}{separator}")
            self.logger.log(level, f"{indent}COMPLETED: {title}")
            self.logger.log(level, f"{indent}{separator}")
            self.section_level -= 1

    def log_exception(self, e, message=None):
        """Log an exception with traceback"""
        if message:
            self.error(f"{message}: {str(e)}")
        else:
            self.error(str(e))
        self.debug(f"Exception details:\n{traceback.format_exc()}")

    def log_command(self, command):
        """Log a command that's about to be executed"""
        if isinstance(command, list):
            cmd_str = ' '.join(command)
        else:
            cmd_str = command
        self.debug(f"Executing command: {cmd_str}")

    def log_result(self, return_code, output):
        """Log the result of a command"""
        status = "SUCCESS" if return_code == 0 else f"FAILED (code: {return_code})"
        self.debug(f"Command {status}")
        if output:
            # Log first few lines of output at debug level
            lines = output.splitlines()
            preview = "\n".join(lines[:5])
            if len(lines) > 5:
                preview += "\n... (output truncated)"
            self.debug(f"Output preview:\n{preview}")

# Singleton pattern to access logger instance globally
logger_instance = Logger()

def get_logger():
    """Get the global logger instance"""
    return logger_instance
