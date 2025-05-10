import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import shutil
from typing import Optional, Dict, Any
import json

# Constants
LOGS_DIR = Path("logs")
MAX_LOG_DAYS = 7
IST = pytz.timezone('Asia/Kolkata')
LOG_FORMAT = {
    'console': '%(asctime)s - %(levelname)s - %(message)s',
    'file': '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
}

def get_current_log_filename() -> str:
    """Get the current log filename with date"""
    current_date = datetime.now(IST).strftime("%Y-%m-%d")
    return f"deals_agent_{current_date}.log"

class CustomFormatter(logging.Formatter):
    """Custom formatter that includes file name and uses IST timezone"""
    
    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        """Convert timestamp to IST timezone"""
        ct = datetime.fromtimestamp(record.created)
        ist_time = ct.astimezone(IST)
        if datefmt:
            return ist_time.strftime(datefmt)
        return ist_time.strftime("%Y-%m-%d %H:%M:%S %Z")

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with file name and line number"""
        # Add file name and line number to the message
        record.file_info = f"{record.filename}:{record.lineno}"
        
        # Add extra fields if they exist
        if hasattr(record, 'extra'):
            extra_str = json.dumps(record.extra)
            record.msg = f"{record.msg} | Extra: {extra_str}"
            
        return super().format(record)

class LoggerManager:
    """Manager class for handling logging operations"""
    
    def __init__(self):
        self.logger = None
        self._setup_logger()
        
    def _setup_logger(self) -> None:
        """Setup and configure the logger with all required handlers"""
        
        # Create logs directory if it doesn't exist
        LOGS_DIR.mkdir(exist_ok=True)
        
        # Configure root logger
        self.logger = logging.getLogger("deals_agent")
        self.logger.setLevel(logging.INFO)
        
        # Remove any existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create formatters
        console_formatter = CustomFormatter(
            LOG_FORMAT['console'],
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_formatter = CustomFormatter(
            LOG_FORMAT['file'],
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console Handler (INFO level)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File Handler with daily rotation
        current_log_file = LOGS_DIR / get_current_log_filename()
        file_handler = TimedRotatingFileHandler(
            current_log_file,
            when="midnight",
            interval=1,
            backupCount=MAX_LOG_DAYS,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.suffix = "%Y-%m-%d.log"  # Format for rotated files
        self.logger.addHandler(file_handler)

        # Set timezone to IST
        logging.Formatter.converter = lambda *args: datetime.now(IST).timetuple()
        
    def cleanup_old_logs(self) -> None:
        """Clean up log files older than MAX_LOG_DAYS"""
        try:
            current_date = datetime.now(IST)
            cutoff_date = current_date - timedelta(days=MAX_LOG_DAYS)
            
            for log_file in LOGS_DIR.glob('deals_agent_*.log*'):
                try:
                    # Get file creation time
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    file_time = IST.localize(file_time)
                    
                    if file_time < cutoff_date:
                        log_file.unlink()
                        self.info(f"Deleted old log file: {log_file}")
                except Exception as e:
                    self.error(f"Error processing log file {log_file}: {str(e)}")
        except Exception as e:
            self.error(f"Error during log cleanup: {str(e)}", exc_info=True)
            
    def _log_with_extra(self, level: int, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Internal method to log with extra fields"""
        if extra is None:
            extra = {}
        self.logger.log(level, msg, extra=extra, **kwargs)
        
    def info(self, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Log info message with optional extra fields"""
        self._log_with_extra(logging.INFO, msg, extra, **kwargs)
        
    def error(self, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Log error message with optional extra fields"""
        self._log_with_extra(logging.ERROR, msg, extra, **kwargs)
        
    def warning(self, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Log warning message with optional extra fields"""
        self._log_with_extra(logging.WARNING, msg, extra, **kwargs)
        
    def debug(self, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Log debug message with optional extra fields"""
        self._log_with_extra(logging.DEBUG, msg, extra, **kwargs)
        
    def critical(self, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Log critical message with optional extra fields"""
        self._log_with_extra(logging.CRITICAL, msg, extra, **kwargs)

# Initialize logger manager
logger_manager = LoggerManager()
logger = logger_manager.logger

# Initial cleanup of old logs
logger_manager.cleanup_old_logs()

# Log initial message
logger.info("Logger initialized with IST timezone and daily log rotation") 