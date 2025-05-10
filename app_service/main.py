import os
import asyncio
import json
import re
from typing import Dict, List, Any, Union, Optional

import uvicorn
import asyncpg # For PostgreSQL database connection
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Path, Depends, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, conlist

# --- CONFIGURATION IMPORTS (ASSUMED) ---
# Assuming db_config.py exists and provides DATABASES and are_db_settings_valid
from db_config import DATABASES, are_db_settings_valid
# Assuming logger_config.py is set up and provides a 'logger' instance
from logger_config import logger

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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY environment variable not set. AI-powered deal suggestions will fail.")

# --- GLOBAL VARIABLES ---
db_pool: Optional[asyncpg.Pool] = None

# --- PYDANTIC MODELS ---

# Database related models
class TableStat(BaseModel):
    table_name: str
    row_count: Union[int, str]  # str for error messages

class DatabaseStatsResponse(BaseModel):
    tables: List[TableStat]
    message: Optional[str] = None

class ColumnDetail(BaseModel):
    column_name: str
    data_type: str
    is_nullable: Optional[str] = None
    column_default: Optional[str] = None

class TableSchemaDetail(BaseModel):
    table_name: str
    columns: List[ColumnDetail]

class SchemaDetailsResponse(BaseModel):
    schema_details: List[TableSchemaDetail]
    message: Optional[str] = None

# AI Deal Suggestion related models
class EventData(BaseModel):
    event_name: str = Field(..., example="City Marathon 2025")
    event_type: str = Field(..., example="Sports")
    date: str = Field(..., example="2025-05-10")
    start_time: str = Field(..., example="07:00")
    location_venue: str = Field(..., example="Central Park")
    expected_attendance: int = Field(..., example=5000)

class InventoryItem(BaseModel):
    sku: str = Field(..., example="UMB-LG-BLK-001")
    product_name: str = Field(..., example="Large Black Umbrella")
    description: str = Field(..., example="A sturdy black umbrella.")
    price: float = Field(..., example=400.00, gt=0)
    quantity_on_hand: int = Field(..., example=150, ge=0)
    category: str = Field(..., example="Accessories")

class DealSuggestionRequest(BaseModel):
    event_details: EventData
    inventory_list: conlist(InventoryItem, min_length=1)

class DealSuggestionResponse(BaseModel):
    suggested_product_sku: str
    deal_details_suggestion_text: str
    suggested_discount_type: str # "fixed_amount" or "percentage"
    suggested_discount_value: float
    original_price: float
    suggested_price: float
    message: str = Field(default="Deal suggestion generated successfully.")

class ErrorResponse(BaseModel):
    error: str
    details: Union[str, List[str], None] = None

# --- FASTAPI APP INITIALIZATION ---
app = FastAPI(
    title="Deals Agent API",
    description="API for deal agent mechanics and database insights.",
    version="1.3.0" # Incremented version for refactor
)

# --- DATABASE HELPER & DEPENDENCY ---
async def get_db_connection():
    """FastAPI dependency to get a database connection from the pool."""
    if not db_pool:
        detail_msg = "Database service is not available. Please check server logs or configuration."
        if not DB_SETTINGS_VALID:
            detail_msg = "Database configuration is invalid or incomplete. Please check server logs."
        elif not db_pool: # Pool creation specifically failed
            detail_msg = "Database service is not available. Connection pool might have failed to initialize."
        logger.error(f"get_db_connection: {detail_msg}")
        raise HTTPException(status_code=503, detail={"message": detail_msg})
    try:
        async with db_pool.acquire() as connection:
            yield connection
    except asyncpg.exceptions.PostgresConnectionError as pce:
        logger.error(f"Failed to acquire DB connection from pool: {pce}", exc_info=True)
        raise HTTPException(status_code=503, detail={"message": "Database connection error occurred while acquiring from pool."})


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

# --- AI SERVICE FUNCTION ---
def generate_deal_from_ai(event_data: EventData, inventory_list: List[InventoryItem]) -> Dict[str, Any]:
    """Generates a product deal suggestion using a generative AI model."""
    if not GEMINI_API_KEY:
        logger.error("AI API Key is not configured.")
        raise ValueError("AI API Key not configured.")

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        generation_config = {
            "temperature": 0.7, "top_p": 0.95, "top_k": 40,
            "max_output_tokens": 1024, "response_mime_type": "application/json",
        }
        safety_settings = [
            {"category": c, "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH",
                      "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]
        ]
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        prompt = f"""
        You are an expert marketing assistant. Analyze event details and inventory to suggest ONE compelling product deal.
        Event: {json.dumps(event_data.model_dump(), indent=2)}
        Inventory: {json.dumps([item.model_dump() for item in inventory_list], indent=2)}

        Select ONE product. Discount should be 10-30% or a meaningful fixed amount.
        'deal_details_suggestion_text' should be catchy, concise, highlight benefit/savings, and relevant to the event.
        'suggested_product_sku' must be from inventory. Use its 'price' as 'original_price'.
        Calculate 'suggested_price'. 'suggested_discount_type' is 'fixed_amount' or 'percentage'.
        If 'percentage', 'suggested_discount_value' is the percent number (e.g., 20 for 20%).
        If 'fixed_amount', 'suggested_discount_value' is currency amount (e.g., 80.00).

        Respond ONLY with a single JSON object:
        {{
          "suggested_product_sku": "string",
          "deal_details_suggestion_text": "string",
          "suggested_discount_type": "string",
          "suggested_discount_value": "float",
          "original_price": "float",
          "suggested_price": "float"
        }}
        Example for a marathon and umbrella:
        {{
          "suggested_product_sku": "UMB-LG-BLK-001",
          "deal_details_suggestion_text": "Beat the rain at the {event_data.event_name}! Large Umbrella, was ₹400, now ₹320! Stay dry. Limited stock!",
          "suggested_discount_type": "fixed_amount",
          "suggested_discount_value": 80.00,
          "original_price": 400.00,
          "suggested_price": 320.00
        }}
        """
        response = model.generate_content(prompt)

        if not response.parts:
            block_reason = "Unknown reason."
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                block_reason = response.prompt_feedback.block_reason_message or str(response.prompt_feedback.block_reason)
            logger.error(f"AI model did not return content. Blocked: {block_reason}")
            raise ValueError(f"AI model response empty/blocked: {block_reason}")

        ai_output_json = response.text
        match = re.search(r"```json\s*([\s\S]*?)\s*```", ai_output_json, re.DOTALL)
        if match:
            ai_output_json = match.group(1)
        
        deal_suggestion = json.loads(ai_output_json)

        # Validation
        selected_sku = deal_suggestion.get("suggested_product_sku")
        inventory_map = {item.sku: item for item in inventory_list}

        if not selected_sku or selected_sku not in inventory_map:
            logger.error(f"AI suggested SKU '{selected_sku}' not in inventory.")
            raise ValueError(f"AI suggested SKU '{selected_sku}' not in inventory.")
        
        actual_item = inventory_map[selected_sku]
        deal_suggestion["original_price"] = actual_item.price # Enforce actual price

        original_price = deal_suggestion["original_price"]
        discount_type = deal_suggestion.get("suggested_discount_type")
        discount_value = float(deal_suggestion.get("suggested_discount_value", 0))
        
        calculated_suggested_price = original_price
        if discount_type == "fixed_amount":
            calculated_suggested_price = original_price - discount_value
        elif discount_type == "percentage":
            calculated_suggested_price = original_price * (1 - discount_value / 100)
        
        # Use calculated price, rounded, and warn if AI's differs significantly
        if abs(deal_suggestion.get("suggested_price", float('inf')) - calculated_suggested_price) > 0.01:
            logger.warning(
                f"AI suggested price {deal_suggestion.get('suggested_price')} differs from "
                f"calculated {calculated_suggested_price:.2f} for SKU {selected_sku}. Using calculated."
            )
        deal_suggestion["suggested_price"] = round(calculated_suggested_price, 2)

        return deal_suggestion

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI JSON response: {e}. Raw: {response.text if 'response' in locals() else 'N/A'}", exc_info=True)
        raise ValueError(f"AI response not valid JSON: {e}")
    except genai.types.generation_types.BlockedPromptException as e:
        logger.error(f"AI prompt blocked: {e}", exc_info=True)
        raise # Re-raise to be caught by endpoint
    except Exception as e:
        logger.error(f"Unexpected AI interaction error: {e}", exc_info=True)
        raise ValueError(f"Unexpected error during AI interaction: {str(e)}")


# --- API ENDPOINTS ---

# Root Endpoint
@app.get("/", summary="Root Path", description="API welcome message and health check.")
async def read_root():
    logger.info("--- Received GET request to / ---")
    return {"message": "Welcome to the Deals Agent API. Visit /docs for API documentation."}

# Database Endpoints
@app.get("/database-stats",
         response_model=DatabaseStatsResponse,
         summary="Get Table Row Counts",
         description="Retrieves 'public' schema tables and their row counts.")
async def get_database_stats(connection: asyncpg.Connection = Depends(get_db_connection)):
    logger.info("--- Received GET request to /database-stats ---")
    table_stats_list: List[Dict[str, Any]] = []
    try:
        tables = await connection.fetch(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
            """
        )
        if not tables:
            logger.info("No tables found in 'public' schema.")
            return DatabaseStatsResponse(tables=[], message="No tables found in 'public' schema.")

        logger.info(f"Found {len(tables)} tables. Querying row counts...")
        for table_record in tables:
            table_name = table_record['table_name']
            current_stat = {"table_name": table_name, "row_count": "Error (unknown)"}
            try:
                query = f'SELECT COUNT(*) AS row_count FROM public."{table_name}";'
                logger.debug(f"Executing count query for table '{table_name}'")
                # Use connection's command_timeout if set, or global default
                count_record = await connection.fetchrow(query, timeout=connection.get_settings().command_timeout)
                current_stat["row_count"] = count_record['row_count'] if count_record else 0
            except asyncpg.exceptions.PostgresSyntaxError as se:
                msg = se.message or se.args[0]
                logger.error(f"Syntax error for table '{table_name}': {msg}")
                current_stat["row_count"] = f"Error (syntax: {msg})"
            except asyncpg.exceptions.InsufficientPrivilegeError as ipe:
                msg = ipe.message or ipe.args[0]
                logger.warning(f"Permission denied for table '{table_name}': {msg}")
                current_stat["row_count"] = "Error (permission denied)"
            except asyncio.TimeoutError: # This should be caught by asyncpg.CommandTimeoutError usually
                logger.error(f"Timeout counting rows for table '{table_name}'.")
                current_stat["row_count"] = "Error (query timeout)"
            except asyncpg.exceptions.CommandTimeoutError: # More specific timeout
                logger.error(f"Command timeout counting rows for table '{table_name}'.")
                current_stat["row_count"] = "Error (command timeout)"
            except Exception as e:
                logger.error(f"Error counting rows for '{table_name}': {type(e).__name__} - {e}", exc_info=False)
                current_stat["row_count"] = f"Error (general: {type(e).__name__})"
            table_stats_list.append(current_stat)
        
        logger.info("Successfully retrieved table statistics.")
        return DatabaseStatsResponse(tables=table_stats_list)

    except Exception as e: # Catch-all for unexpected issues with the overall process
        logger.error(f"Unexpected server error during /database-stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"message": "An unexpected server error occurred."})

@app.get("/table-schema/{table_prefix}",
         response_model=SchemaDetailsResponse,
         summary="Get Table Schema by Prefix",
         description="Retrieves schema for 'public' tables matching a prefix.")
async def get_table_schema_by_prefix(
    table_prefix: str = Path(..., description="Prefix to filter table names (e.g., 'deals_agent'). Case-sensitive."),
    connection: asyncpg.Connection = Depends(get_db_connection)
):
    logger.info(f"--- Received GET request to /table-schema/{table_prefix} ---")
    schema_details_list: List[TableSchemaDetail] = []
    try:
        query_tables = """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
              AND table_name LIKE $1 || '%'
            ORDER BY table_name;
        """
        logger.debug(f"Fetching tables with prefix '{table_prefix}'")
        matching_tables = await connection.fetch(query_tables, table_prefix)

        if not matching_tables:
            logger.info(f"No tables found with prefix '{table_prefix}'.")
            return SchemaDetailsResponse(
                schema_details=[],
                message=f"No tables found in 'public' schema starting with '{table_prefix}'."
            )

        logger.info(f"Found {len(matching_tables)} tables. Querying column details...")
        for table_record in matching_tables:
            table_name = table_record['table_name']
            logger.debug(f"Fetching schema for table: {table_name}")
            query_columns = """
                SELECT column_name, udt_name AS data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = $1
                ORDER BY ordinal_position;
            """
            column_records = await connection.fetch(query_columns, table_name)
            columns_list = [ColumnDetail(**col) for col in column_records]
            schema_details_list.append(TableSchemaDetail(table_name=table_name, columns=columns_list))
            logger.debug(f"Fetched {len(columns_list)} columns for table '{table_name}'.")

        logger.info(f"Successfully retrieved schema for tables with prefix '{table_prefix}'.")
        return SchemaDetailsResponse(
            schema_details=schema_details_list,
            message=f"Schema details for tables starting with '{table_prefix}'."
        )
    except Exception as e:
        logger.error(f"Unexpected server error during /table-schema/{table_prefix}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"message": "An unexpected server error occurred."})

# AI Deal Suggestion Endpoint
@app.post("/suggest-deal/",
          response_model=DealSuggestionResponse,
          responses={500: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
          summary="Suggest Product Deal",
          description="Suggests a product deal using AI based on event and inventory.")
async def suggest_product_deal(request_data: DealSuggestionRequest = Body(...)):
    logger.info(f"--- Received POST request to /suggest-deal/ for event: {request_data.event_details.event_name} ---")
    if not GEMINI_API_KEY:
        logger.error("Attempted /suggest-deal/ call with no GEMINI_API_KEY configured.")
        raise HTTPException(status_code=500, detail={"error": "Internal Server Error", "details": "AI API Key is not configured on the server."})

    try:
        deal_suggestion_data = generate_deal_from_ai(
            request_data.event_details,
            request_data.inventory_list
        )
        logger.info(f"Successfully generated deal suggestion for SKU: {deal_suggestion_data.get('suggested_product_sku')}")
        return DealSuggestionResponse(**deal_suggestion_data)
    except ValueError as ve: # From generate_deal_from_ai (JSON parsing, validation, API key missing there)
        logger.warning(f"ValueError in AI suggestion processing: {ve}", exc_info=True)
        raise HTTPException(status_code=400, detail={"error": "Error processing AI suggestion", "details": str(ve)})
    except genai.types.generation_types.BlockedPromptException as bpe:
        block_reason = "Prompt was blocked by AI safety filters."
        if hasattr(bpe, 'response') and hasattr(bpe.response, 'prompt_feedback') and bpe.response.prompt_feedback:
            block_reason += f" Reason: {bpe.response.prompt_feedback.block_reason_message or bpe.response.prompt_feedback.block_reason}"
        logger.warning(f"AI prompt blocked: {block_reason}", exc_info=True)
        raise HTTPException(status_code=400, detail={"error": "AI Generation Blocked", "details": block_reason})
    except Exception as e:
        logger.error(f"Generic exception in /suggest-deal/ endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"error": "Internal Server Error", "details": "An unexpected error occurred while generating the deal suggestion."})


# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    # Determine the module name for uvicorn (e.g., "main" if this file is main.py)
    module_name = os.path.splitext(os.path.basename(__file__))[0]
    
    server_port_str = os.environ.get("PORT", "8008")
    try:
        server_port = int(server_port_str)
    except ValueError:
        logger.warning(f"Invalid SERVER_PORT: '{server_port_str}'. Defaulting to 8008.")
        server_port = 8008

    logger.info(f"Starting Uvicorn server for '{module_name}:app' on 0.0.0.0:{server_port}")
    uvicorn.run(f"{module_name}:app", host="0.0.0.0", port=server_port, reload=True)