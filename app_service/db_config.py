# config.py
import os
from dotenv import load_dotenv # Optional: for loading .env file for local development

# Load environment variables from .env file if it exists (especially for local development)
# In a production environment, these variables are typically set directly in the environment.
load_dotenv()

logger_config_py_content = """
# logger_config.py
import logging
import sys

# Create logger
logger = logging.getLogger("db_stats_api") # Changed logger name for clarity
logger.setLevel(logging.DEBUG) # Set default logging level

# Create console handler and set level to debug
ch = logging.StreamHandler(sys.stdout) # Output to stdout
ch.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')

# Add formatter to ch
ch.setFormatter(formatter)

# Add ch to logger
# Avoid adding handler multiple times if this script is re-imported or logger is already configured
if not logger.handlers:
    logger.addHandler(ch)

# Example usage (optional, for testing the logger directly)
# if __name__ == "__main__":
#     logger.debug("Debug message from logger_config")
#     logger.info("Info message from logger_config")
#     logger.warning("Warning message from logger_config")
#     logger.error("Error message from logger_config")
#     logger.critical("Critical message from logger_config")
"""

# --- Database Configuration ---
# We'll define a dictionary to hold connection parameters for one or more databases.
# Here, we'll use a 'default' key for the primary database.

DATABASES = {
    'default': {
        'ENGINE': 'asyncpg',  # Specifying the engine, useful if you support multiple DB types
        'NAME': os.environ.get("DATABASE_NAME"),
        'USER': os.environ.get("DATABASE_USER"),
        'PASSWORD': os.environ.get("DATABASE_PASSWORD"),
        'HOST': os.environ.get("DATABASE_HOST"),
        'PORT': os.environ.get("DATABASE_PORT", "5432"), # Default PostgreSQL port as string
    }
    # You could add other database configurations here if needed:
    # 'read_replica': { ... }
}

# --- Other Configurations (Example) ---
# You can add other configurations here as your application grows.
# For example, API keys, external service URLs, etc.
# BUNNYCDN_ACCESS_KEY = os.environ.get("BUNNYCDN_ACCESS_KEY")

# --- Validate Database Port ---
# Ensure the port is an integer if provided, otherwise log an error or raise one.
try:
    if DATABASES['default']['PORT']:
        DATABASES['default']['PORT'] = int(DATABASES['default']['PORT'])
    else:
        # If DATABASE_PORT is not set or empty, it will default to 5432 (string) above,
        # then int(None) or int("") would fail. So we handle it.
        # However, asyncpg can often handle string port numbers, but it's cleaner as int.
        DATABASES['default']['PORT'] = 5432 # Explicitly set default if empty or None
except ValueError:
    # This import is local to this try-except block to avoid circular dependency issues
    # if logger_config is also trying to import something from config.
    # However, for simple logging, it's generally fine.
    from logger_config import logger
    logger.error(
        f"Invalid DATABASE_PORT: '{os.environ.get('DATABASE_PORT')}'. "
        f"It must be a valid integer. Using default 5432."
    )
    DATABASES['default']['PORT'] = 5432 # Fallback to default port on error

# --- Function to check if essential DB settings are present ---
def are_db_settings_valid(db_alias: str = 'default') -> bool:
    """Checks if essential database settings for the given alias are present."""
    db_config = DATABASES.get(db_alias)
    if not db_config:
        return False
    required_keys = ['NAME', 'USER', 'HOST', 'PORT'] # Password can be None for some auth methods
    return all(db_config.get(key) is not None for key in required_keys)

if __name__ == '__main__':
    # This block is for testing the config.py file directly
    # It's good practice to ensure your config loads correctly.
    from logger_config import logger # Placed here for standalone testing
    logger.info("--- Testing config.py ---")
    logger.info(f"Database settings for 'default': {DATABASES['default']}")
    logger.info(f"Essential DB settings valid for 'default': {are_db_settings_valid('default')}")
    # logger.info(f"BunnyCDN Access Key: {'Set' if BUNNYCDN_ACCESS_KEY else 'Not Set'}")
    logger.info("--- End of config.py test ---")



