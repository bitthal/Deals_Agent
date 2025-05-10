from fastapi import Depends
import asyncpg
from logger_config import logger

from config.database import DATABASES, are_db_settings_valid

# Global connection pool
db_pool = None

async def get_db_connection() -> asyncpg.Connection:
    """
    Get a database connection from the pool.
    """
    global db_pool
    
    if not db_pool:
        if not are_db_settings_valid('default'):
            logger.error("Database settings are invalid. Cannot create connection pool.")
            raise Exception("Database configuration is invalid")
            
        db_config = DATABASES['default']
        try:
            db_pool = await asyncpg.create_pool(
                user=db_config['USER'],
                password=db_config.get('PASSWORD'),
                database=db_config['NAME'],
                host=db_config['HOST'],
                port=db_config['PORT'],
                min_size=1,
                max_size=10
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {str(e)}")
            raise
    
    try:
        async with db_pool.acquire() as connection:
            yield connection
    except Exception as e:
        logger.error(f"Error acquiring database connection: {str(e)}")
        raise 