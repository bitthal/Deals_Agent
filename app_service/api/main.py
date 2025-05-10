import os
import asyncio
import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from logger_config import logger

from config.database import DATABASES, are_db_settings_valid
from config.settings import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    GEMINI_API_KEY,
    GEMINI_MODEL_NAME
)

from .routers import database, deals
from .dependencies.database import db_pool

# --- APPLICATION CONFIGURATION ---
logger.info("--- Initializing Application ---")

# Database Configuration Validation
DB_CONFIG = DATABASES.get('default')
DB_SETTINGS_VALID = False
if not DB_CONFIG:
    logger.critical("FATAL: 'default' database configuration not found. Application may not function correctly with DB features.")
else:
    DB_SETTINGS_VALID = are_db_settings_valid('default')
    logger.info(f"DATABASE_ENGINE: {DB_CONFIG.get('ENGINE')}")
    logger.info(f"DATABASE_NAME: {'Set' if DB_CONFIG.get('NAME') else 'Not Set'}")
    logger.info(f"DATABASE_USER: {'Set' if DB_CONFIG.get('USER') else 'Not Set'}")
    logger.info(f"DATABASE_PASSWORD: {'Set' if DB_CONFIG.get('PASSWORD') else 'Not Set (or empty)'}")
    logger.info(f"DATABASE_HOST: {'Set' if DB_CONFIG.get('HOST') else 'Not Set'}")
    logger.info(f"DATABASE_PORT: {DB_CONFIG.get('PORT') if DB_CONFIG.get('PORT') is not None else 'Invalid/Not Set'}")
    logger.info(f"Overall database settings validity for 'default': {DB_SETTINGS_VALID}")

# AI Configuration
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY environment variable not set. AI-powered deal suggestions will fail.")

# --- FASTAPI APP INITIALIZATION ---
app = FastAPI(
    title="Deals Agent API",
    description="API for managing deals and suggestions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(database.router)
app.include_router(deals.router)

# Root Endpoint
@app.get("/", summary="Root Path", description="API welcome message and health check.")
async def read_root():
    logger.info("--- Received GET request to / ---")
    return {"message": "Welcome to Deals Agent API"}

# --- FASTAPI EVENT HANDLERS ---
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup: FastAPI server is starting.")
    global db_pool
    
    if not DB_SETTINGS_VALID or not DB_CONFIG:
        logger.error("Database configuration (from config.py) is incomplete or invalid. DB pool will not be created.")
        return

    logger.info(
        f"Attempting to create DB connection pool for "
        f"{DB_CONFIG['USER']}@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['NAME']}"
    )
    try:
        db_pool = await asyncpg.create_pool(
            user=DB_CONFIG['USER'],
            password=DB_CONFIG.get('PASSWORD'),
            database=DB_CONFIG['NAME'],
            host=DB_CONFIG['HOST'],
            port=DB_CONFIG['PORT'],
            min_size=1,
            max_size=10,
            timeout=10, # Connection timeout
            command_timeout=15 # Default command timeout
        )
        async with db_pool.acquire() as conn: # Test connection
            db_version = await conn.fetchval("SELECT version();")
            logger.info(f"Database connection pool created successfully. PostgreSQL Version: {db_version}")
    except Exception as e:
        logger.error(f"Failed to create database connection pool: {e}", exc_info=True)
        db_pool = None # Ensure pool is None if creation fails

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown: Server is shutting down.")
    if db_pool:
        logger.info("Closing database connection pool...")
        await db_pool.close()
        logger.info("Database connection pool closed.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True) 