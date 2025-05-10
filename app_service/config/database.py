import os
from dotenv import load_dotenv
from logger_config import logger

# Load environment variables from .env file if it exists
load_dotenv()

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'asyncpg',
        'NAME': os.environ.get("DATABASE_NAME"),
        'USER': os.environ.get("DATABASE_USER"),
        'PASSWORD': os.environ.get("DATABASE_PASSWORD"),
        'HOST': os.environ.get("DATABASE_HOST"),
        'PORT': os.environ.get("DATABASE_PORT", "5432"),
    }
}

# Validate Database Port
try:
    if DATABASES['default']['PORT']:
        DATABASES['default']['PORT'] = int(DATABASES['default']['PORT'])
    else:
        DATABASES['default']['PORT'] = 5432
except ValueError:
    logger.error(
        f"Invalid DATABASE_PORT: '{os.environ.get('DATABASE_PORT')}'. "
        f"It must be a valid integer. Using default 5432."
    )
    DATABASES['default']['PORT'] = 5432

def are_db_settings_valid(db_alias: str = 'default') -> bool:
    """Checks if essential database settings for the given alias are present."""
    db_config = DATABASES.get(db_alias)
    if not db_config:
        return False
    required_keys = ['NAME', 'USER', 'HOST', 'PORT']
    return all(db_config.get(key) is not None for key in required_keys) 