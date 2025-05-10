import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import shutil
from typing import Optional

# Constants
LOGS_DIR = Path("logs")
MAX_LOG_DAYS = 7
IST = pytz.timezone('Asia/Kolkata')

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
        return super().format(record)

def setup_logger() -> logging.Logger:
    """Setup and configure the logger with all required handlers"""
    
    # Create logs directory if it doesn't exist
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger("deals_agent")
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File Handler (INFO level)
    file_handler = RotatingFileHandler(
        LOGS_DIR / "deals_agent.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Set timezone to IST
    logging.Formatter.converter = lambda *args: datetime.now(IST).timetuple()
    
    return logger

def cleanup_old_logs() -> None:
    """Clean up log files older than MAX_LOG_DAYS"""
    try:
        # Get current time in IST
        current_date = datetime.now(IST)
        cutoff_date = current_date - timedelta(days=MAX_LOG_DAYS)
        
        for log_file in LOGS_DIR.glob('*.log*'):
            try:
                # Extract date from filename (assuming format log_YYYY-MM-DD.log)
                file_date_str = log_file.stem.split('_')[-1]
                # Create timezone-aware datetime for the file date
                file_date = datetime.strptime(file_date_str, '%Y-%m-%d')
                file_date = IST.localize(file_date)
                
                if file_date < cutoff_date:
                    log_file.unlink()
                    logger.info(f"Deleted old log file: {log_file}")
            except (ValueError, IndexError):
                # Skip files that don't match the expected format
                continue
    except Exception as e:
        logger.error(f"Error during log cleanup: {e}", exc_info=True)

# Initialize logger
logger = setup_logger()

# Initial cleanup of old logs
cleanup_old_logs()

# Log initial message
logger.info("Logger initialized with IST timezone and automatic log rotation") 