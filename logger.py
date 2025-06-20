import logging
import os
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self):
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Configure logging
        self.logger = logging.getLogger('facebook_bot')
        self.logger.setLevel(logging.INFO)
        
        # Create handlers
        # File handler for all logs
        file_handler = RotatingFileHandler(
            'logs/facebook_bot.log',
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        
        # Error file handler
        error_handler = RotatingFileHandler(
            'logs/errors.log',
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        
        # Create formatters and add it to handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        
        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message, exc_info=True):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)

# Create global logger instance
logger = Logger()
