import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Application Settings
APP_NAME = "Deals Agent API"
APP_VERSION = "1.3.0"
APP_DESCRIPTION = "API for deal agent mechanics and database insights."

# Server Settings
DEFAULT_PORT = 8008
HOST = "0.0.0.0"

# AI Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = "gemini-1.5-flash-latest"

# Logging Settings
LOG_LEVEL = "DEBUG"
LOG_FORMAT = '%(asctime)s [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S %Z%z'
LOG_DIRECTORY = "logs"
LOG_BACKUP_COUNT = 30 