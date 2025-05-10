import logging
import os
import glob
import sys  # Required for stderr output
from logging.handlers import RotatingFileHandler # Base class FileHandler is sufficient
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo # Requires Python 3.9+ and tzdata package
from typing import Optional, List, Tuple, Union

# --- Configuration ---
LOG_DIRECTORY_NAME = 'logs' # Name of the subdirectory for logs
BACKUP_COUNT = 30 # Number of days/log files to keep
LOG_LEVEL = logging.DEBUG # Logging level for the handler/logger
LOG_FORMAT = '%(asctime)s [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S %Z%z' # Format for timestamps within the log file

# --- Timezone Definition ---
try:
    # Use Asia/Kolkata timezone (IST)
    APP_TZ = ZoneInfo("Asia/Kolkata")
except Exception as e:
    print(f"CRITICAL: Failed to load Timezone 'Asia/Kolkata'. Using UTC as fallback. Error: {e}", file=sys.stderr)
    # Fallback to UTC if zoneinfo fails
    APP_TZ = ZoneInfo("UTC")

# --- Custom IST Formatter ---
class ISTFormatter(logging.Formatter):
    """
    Custom logging Formatter that uses the application timezone (APP_TZ)
    for timestamps in log records.
    """
    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        """
        Return the creation time of the specified LogRecord as formatted text
        in the configured application timezone (APP_TZ).
        """
        dt = datetime.fromtimestamp(record.created, tz=APP_TZ)
        if datefmt:
            # Use the specified date format
            return dt.strftime(datefmt)
        # Default to ISO 8601 format with timezone offset if no format specified
        try:
             # Attempt ISO 8601 format first
             return dt.isoformat(timespec='milliseconds')
        except AttributeError:
             # Fallback for older Python versions potentially lacking timespec
             return dt.strftime('%Y-%m-%dT%H:%M:%S.%f%z')


# --- Custom Dated File Handler ---
class DatedFileHandler(logging.FileHandler):
    """
    A custom logging.FileHandler that creates a new log file daily based on APP_TZ,
    names files like 'processing_YYYY-MM-DD.log', automatically switches at
    midnight (APP_TZ), and retains a specified number of backup logs.
    """
    def __init__(self, log_dir: str, backup_count: int, encoding: str = 'utf-8', delay: bool = False):
        """
        Initializes the handler.

        Args:
            log_dir (str): The directory where log files will be stored.
            backup_count (int): The number of old log files to retain.
            encoding (str): The character encoding for log files. Defaults to 'utf-8'.
            delay (bool): If true, file opening is deferred until the first call to emit(). Defaults to False.
        """
        self.log_dir = os.path.abspath(log_dir) # Store absolute path
        self.backup_count = max(1, backup_count) # Ensure at least 1 backup is kept conceptually (current file)
        self.encoding = encoding
        self.log_file_prefix = "processing_"
        self.log_file_suffix = ".log"
        self.date_format = "%Y-%m-%d" # Format for the date in the filename

        # Ensure the log directory exists before proceeding
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            # print(f"DEBUG: Log directory ensured: {self.log_dir}") # Uncomment for debugging
        except OSError as e:
            # Log to stderr if directory creation fails critically
            print(f"CRITICAL ERROR: Could not create log directory {self.log_dir}: {e}", file=sys.stderr)
            raise # Re-raise error as logging cannot proceed without the directory

        # Determine the current date in the application timezone
        now = datetime.now(tz=APP_TZ)
        self.current_date = now.date()

        # Construct the initial filename
        base_filename = self._get_filename(self.current_date)

        # Initialize the parent FileHandler
        super().__init__(base_filename, mode='a', encoding=self.encoding, delay=delay)

        # Perform initial cleanup of old logs on startup
        if self.backup_count > 0:
            self._clean_old_logs()

    def _get_filename(self, log_date: date) -> str:
        """Constructs the full log filename path for a given date."""
        return os.path.join(
            self.log_dir,
            f'{self.log_file_prefix}{log_date.strftime(self.date_format)}{self.log_file_suffix}'
        )

    def _clean_old_logs(self) -> None:
        """Removes log files older than the configured backup_count."""
        if self.backup_count <= 0: # No cleanup needed if backup_count is zero or negative
             return

        # print(f"DEBUG: Starting log cleanup in {self.log_dir} (keeping {self.backup_count} files)...") # Uncomment for debugging
        try:
            log_files: List[Tuple[date, str]] = []
            # Construct the pattern to find log files generated by this handler
            pattern = os.path.join(self.log_dir, f"{self.log_file_prefix}*{self.log_file_suffix}")

            # Find all files matching the pattern
            for filepath in glob.glob(pattern):
                filename = os.path.basename(filepath)
                # Extract the date string from the filename
                date_str = filename[len(self.log_file_prefix):-len(self.log_file_suffix)]
                try:
                    # Convert the date string to a date object
                    log_date = datetime.strptime(date_str, self.date_format).date()
                    log_files.append((log_date, filepath))
                except ValueError:
                    # Ignore files with unexpected date formats in the name
                    # print(f"DEBUG: Ignoring file with non-matching date format: {filepath}") # Uncomment for debugging
                    continue

            # Sort log files by date (oldest first)
            log_files.sort(key=lambda x: x[0])

            # Determine how many files need to be deleted
            files_to_delete_count = len(log_files) - self.backup_count
            if files_to_delete_count > 0:
                files_to_delete = log_files[:files_to_delete_count]
                # print(f"DEBUG: Found {len(log_files)} log files. Deleting {files_to_delete_count} oldest files.") # Uncomment for debugging
                for log_date, filepath in files_to_delete:
                    try:
                        os.remove(filepath)
                        # print(f"DEBUG: Deleted old log file: {filepath}") # Uncomment for debugging
                    except OSError as e:
                        # Log deletion errors to stderr
                        print(f"ERROR: Could not delete log file {filepath}: {e}", file=sys.stderr)
                        # Optionally log this error using a fallback mechanism if needed
            # else:
                # print(f"DEBUG: Found {len(log_files)} log files. No deletion needed (backup count: {self.backup_count}).") # Uncomment for debugging

        except Exception as e:
            # Log any other errors during cleanup to stderr
            print(f"ERROR: An unexpected error occurred during log cleanup: {e}", file=sys.stderr)

    def switch_file(self, new_date: date) -> None:
        """
        Closes the current log file, opens a new one for the new_date,
        and triggers cleanup of old logs.
        """
        # print(f"DEBUG: Switching log file. Current date: {self.current_date}, New date: {new_date}") # Uncomment for debugging
        self.current_date = new_date
        new_filename = self._get_filename(new_date)

        # Close the current stream cleanly before switching
        if self.stream:
            try:
                self.stream.flush()
                self.stream.close()
            except Exception as e:
                 print(f"ERROR: Exception occurred while closing stream for {self.baseFilename}: {e}", file=sys.stderr)
            finally:
                 self.stream = None # Ensure stream is marked as closed/None

        # Update the baseFilename for the parent class
        self.baseFilename = new_filename

        # Explicitly open the new log file stream.
        # This ensures the file is ready immediately after the switch.
        try:
            self.stream = self._open()
            # print(f"DEBUG: Opened new log file: {self.baseFilename}") # Uncomment for debugging
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to open new log file {self.baseFilename}: {e}", file=sys.stderr)
            # Handle this critical error appropriately - maybe try logging to stderr?
            # Depending on the application, you might need to disable logging or halt.
            self.stream = None # Ensure stream is None if open failed

        # Clean up old logs after switching to the new file
        if self.backup_count > 0:
            self._clean_old_logs()


    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a record. Checks if the date has changed (based on APP_TZ)
        and switches the log file if necessary before emitting.
        """
        try:
            # Determine the date of the record in the application timezone
            record_time = datetime.fromtimestamp(record.created, tz=APP_TZ)
            record_date = record_time.date()

            # Check if the date has changed compared to the handler's current date
            if record_date != self.current_date:
                self.switch_file(record_date)

            # Ensure the stream is available before emitting.
            # While switch_file should handle opening, this adds a layer of safety,
            # especially if 'delay=True' was used or if an error occurred during switch_file.
            if self.stream is None:
                try:
                     self.stream = self._open() # Attempt to open/reopen the stream
                except Exception as e:
                     print(f"ERROR: Failed to open/reopen stream in emit for {self.baseFilename}: {e}", file=sys.stderr)
                     self.handleError(record) # Use standard error handling
                     return # Cannot proceed without a stream

            # If the stream is ready, proceed with the default emit behaviour
            super().emit(record)

        except Exception:
            # Handle any unexpected errors during the emit process
            self.handleError(record)

# --- Logger Setup ---
def setup_logging():
    """Configures the root logger with the DatedFileHandler and ISTFormatter."""

    # Determine the absolute path for the log directory relative to this script file
    try:
        # __file__ should give the path to script_3_logger_config.py
        _current_script_path = os.path.abspath(__file__)
        _current_dir = os.path.dirname(_current_script_path)
        log_dir_path = os.path.join(_current_dir, LOG_DIRECTORY_NAME)
    except NameError:
        # Fallback if __file__ is not defined (e.g., interactive session)
        print("WARNING: Could not determine script path via __file__. Using current working directory for logs.", file=sys.stderr)
        log_dir_path = os.path.join(os.getcwd(), LOG_DIRECTORY_NAME)


    # print(f"DEBUG: Attempting to configure logger. Log directory: {log_dir_path}") # Uncomment for debugging

    # Get the root logger instance
    # Consider using a specific named logger ('my_app') instead of the root logger
    # if this is part of a larger application or library to avoid conflicts.
    # logger = logging.getLogger('my_app')
    logger = logging.getLogger() # Get the root logger

    # Prevent adding handlers multiple times if this setup function is called again
    # or if the module is reloaded in some environments.
    if any(isinstance(h, DatedFileHandler) for h in logger.handlers):
        # print("DEBUG: DatedFileHandler already configured for this logger.") # Uncomment for debugging
        return logger # Return the already configured logger

    try:
        # 1. Create the Custom Dated File Handler instance
        file_handler = DatedFileHandler(
            log_dir=log_dir_path,
            backup_count=BACKUP_COUNT,
            encoding='utf-8'
        )

        # 2. Create the Custom Timezone Formatter instance
        formatter = ISTFormatter(
            fmt=LOG_FORMAT,
            datefmt=DATE_FORMAT
        )

        # 3. Set the formatter for the handler
        file_handler.setFormatter(formatter)

        # 4. Set the logging level for the handler (optional, can also set on logger)
        # file_handler.setLevel(LOG_LEVEL) # Usually set level on logger

        # 5. Add the handler to the logger
        logger.addHandler(file_handler)

        # 6. Set the overall logging level for the logger
        # Messages below this level will be ignored entirely
        logger.setLevel(LOG_LEVEL)

        # Optional: Add a StreamHandler to output logs to console as well (useful for debugging)
        # console_handler = logging.StreamHandler(sys.stdout)
        # console_handler.setFormatter(formatter)
        # console_handler.setLevel(logging.INFO) # Maybe log only INFO+ to console
        # if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        #     logger.addHandler(console_handler)

        # print("DEBUG: Logger configuration successful.") # Uncomment for debugging

    except Exception as e:
        # Catch-all for any error during the setup process
        print(f"CRITICAL ERROR DURING LOGGER SETUP: {e}", file=sys.stderr)
        # Fallback: Configure a basic console logger if setup fails
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s [%(levelname)s] %(message)s')
        logger.error(f"Failed to configure DatedFileHandler due to: {e}. Using basic console logging.", exc_info=True)
        # Depending on requirements, you might re-raise the exception:
        # raise

    return logger

# --- Initialize logging when this module is imported ---
# Call setup_logging() directly or provide a function to be called by the main application
logger = setup_logging()

# Example Usage (if running this file directly for testing)
if __name__ == "__main__":
    print("Running logger configuration directly for testing...")
    logger = setup_logging()

    # Check if handler was added (useful after setup_logging call)
    print(f"Logger '{logger.name}' handlers: {logger.handlers}")
    if not logger.handlers:
         print("ERROR: No handlers were successfully added to the logger.")
    else:
         print(f"Logging level set to: {logging.getLevelName(logger.level)}")
         # Test logging messages
         logger.debug("This is a debug message.")
         logger.info("This is an info message.")
         logger.warning("This is a warning message.")
         logger.error("This is an error message.")
         logger.critical("This is a critical message.")

         print(f"\nLog files should be generated in: {os.path.abspath(os.path.join(os.path.dirname(__file__), LOG_DIRECTORY_NAME))}")
         print("Check the log file for the messages.")

    # Example of getting a logger elsewhere in an application:
    # import logging
    # some_other_module_logger = logging.getLogger('my_app.some_module') # If using named loggers
    # some_other_module_logger.info("Log message from another module")


# --- End of script_3_logger_config.py ---