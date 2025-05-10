import os
import logging
import logging.handlers
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
    logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = CustomFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(file_info)s - %(message)s'
    )
    simple_formatter = CustomFormatter(
        '%(asctime)s - %(levelname)s - %(file_info)s - %(message)s'
    )
    
    # Console Handler (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File Handler (DEBUG level)
    current_date = datetime.now(IST).strftime('%Y-%m-%d')
    log_file = LOGS_DIR / f"log_{current_date}.log"
    
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',
        interval=1,
        backupCount=MAX_LOG_DAYS,
        encoding='utf-8',
        atTime=datetime.strptime('00:00', '%H:%M').time()
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Error File Handler (ERROR level)
    error_log_file = LOGS_DIR / f"error_{current_date}.log"
    error_file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=error_log_file,
        when='midnight',
        interval=1,
        backupCount=MAX_LOG_DAYS,
        encoding='utf-8',
        atTime=datetime.strptime('00:00', '%H:%M').time()
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_file_handler)
    
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