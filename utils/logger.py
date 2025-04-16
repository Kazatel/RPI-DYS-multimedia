import logging
import os
from datetime import datetime
import config


class Logger:
    def __init__(self, log_dir=config.LOG_DIR, console_level=logging.INFO, file_level=logging.DEBUG):
        # Basic setup
        self.logger = logging.getLogger("app_logger")
        self.logger.setLevel(logging.DEBUG)
        
        # Create log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"rpi_dys_multimedia.log")
        self.log_file_path = log_file

        # Setup handlers
        self.file_handler = logging.FileHandler(log_file)
        self.file_handler.setLevel(file_level)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(file_formatter)
        
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(console_level)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        self.console_handler.setFormatter(console_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)
    
    # Regular logging methods
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
        self.p_info(
            f"📡 You can monitor progress in another terminal with:\n"
            f"    tail -f {self.log_file_path}"
        )