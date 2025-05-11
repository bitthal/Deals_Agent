import asyncio
import asyncpg
import aiohttp
from datetime import datetime
import os
import sys
from pathlib import Path
from models import Event

# Add the parent directory to Python path to import the centralized logger
sys.path.append(str(Path(__file__).parent.parent.parent))
from logger_config import logger

# Ensure log directory exists
log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Database connection settings
DB_USER = os.getenv("DATABASE_USER", "deals_user")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "deals_password")
DB_NAME = os.getenv("DATABASE_NAME", "deals_db")
DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = int(os.getenv("DATABASE_PORT", 5432))

# API settings
API_HOST = os.getenv("API_HOST", "app")
API_PORT = int(os.getenv("API_PORT", 8008))
DEAL_SUGGESTION_ENDPOINT = f"http://{API_HOST}:{API_PORT}/deals/suggest"

QUERY_UNPROCESSED = """
    SELECT * FROM events WHERE processed_for_suggestion = FALSE
"""

QUERY_INVENTORY = """
    SELECT * FROM inventory WHERE vendor_id = $1
"""

UPDATE_PROCESSED = """
    UPDATE events SET processed_for_suggestion = TRUE WHERE id = $1
"""

async def prepare_deal_suggestion_payload(event: Event, inventory_items: list) -> dict:
    """Prepare the payload for the deal suggestion API"""
    return {
        "event_data": {
            "vendor_id": event.vendor_id,
            "location_uuid": event.location_uuid,
            "event_trigger_point": event.event_trigger_point,
            "event_details_text": event.event_details_text,
            "event_location_latitude": float(event.event_location_latitude),
            "event_location_longitude": float(event.event_location_longitude),
            "event_timestamp": event.event_timestamp.isoformat()
        },
        "inventory_items": [
            {
                "sku": item["sku"],
                "product_name": item["product_name"],
                "description": item["description"],
                "price": float(item["price"]),
                "quantity_on_hand": item["quantity_on_hand"],
                "category": item["category"],
                "supplier": item["supplier"]
            }
            for item in inventory_items
        ]
    }

async def call_deal_suggestion_api(payload: dict) -> dict:
    """Call the deal suggestion API"""
    logger.info(f"Attempting to connect to API at {DEAL_SUGGESTION_ENDPOINT}")
    async with aiohttp.ClientSession() as session:
        try:
            logger.info("Making POST request to API")
            async with session.post(DEAL_SUGGESTION_ENDPOINT, json=payload) as response:
                logger.info(f"Received response with status {response.status}")
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"API call failed with status {response.status}", extra={
                        "error": error_text,
                        "status_code": response.status
                    })
                    return None
        except Exception as e:
            logger.error("Error calling deal suggestion API", extra={
                "error": str(e),
                "endpoint": DEAL_SUGGESTION_ENDPOINT,
                "payload": payload
            }, exc_info=True)
            return None

async def process_events():
    """Process unprocessed events from the database"""
    conn = None
    try:
        logger.info("Starting event processing cycle", extra={
            "db_host": DB_HOST,
            "db_name": DB_NAME,
            "db_user": DB_USER
        })
        
        conn = await asyncpg.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT
        )
        
        events = await conn.fetch(QUERY_UNPROCESSED)
        event_count = len(events)
        
        if not events:
            logger.info("No unprocessed events found")
            return
            
        logger.info(f"Found {event_count} unprocessed events", extra={
            "event_count": event_count
        })
        
        for record in events:
            try:
                event = Event.from_db_record(record)
                logger.info("Processing event", extra={
                    "event_id": event.id,
                    "event_type": event.event_trigger_point,
                    "event_data": event.event_details_text
                })
                
                # Get inventory items for the vendor
                inventory_items = await conn.fetch(QUERY_INVENTORY, event.vendor_id)
                
                # Prepare payload for deal suggestion API
                payload = await prepare_deal_suggestion_payload(event, inventory_items)
                
                # Call deal suggestion API
                api_response = await call_deal_suggestion_api(payload)
                
                if api_response:
                    logger.info("Successfully called deal suggestion API", extra={
                        "event_id": event.id,
                        "api_response": api_response
                    })
                    
                    # Mark event as processed
                    await conn.execute(UPDATE_PROCESSED, event.id)
                    logger.info("Event marked as processed", extra={
                        "event_id": event.id,
                        "processed_at": datetime.utcnow().isoformat()
                    })
                else:
                    logger.error("Failed to get response from deal suggestion API", extra={
                        "event_id": event.id
                    })
                
            except Exception as e:
                logger.error("Error processing individual event", extra={
                    "event_id": record.get('id'),
                    "error": str(e)
                }, exc_info=True)
                
    except Exception as e:
        logger.error("Error in event processing cycle", extra={
            "error": str(e),
            "db_host": DB_HOST,
            "db_name": DB_NAME
        }, exc_info=True)
    finally:
        if conn:
            await conn.close()
            logger.debug("Database connection closed")

async def main():
    """Main function to run the event processing agent"""
    logger.info("Event Processing Agent started", extra={
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    })
    
    while True:
        try:
            await process_events()
            logger.info("Sleeping for 2 minutes before next cycle")
            await asyncio.sleep(2 * 60)
        except Exception as e:
            logger.error("Error in main loop", extra={
                "error": str(e)
            }, exc_info=True)
            # Wait a bit before retrying after an error
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Event Processing Agent stopped by user")
    except Exception as e:
        logger.critical("Event Processing Agent crashed", extra={
            "error": str(e)
        }, exc_info=True) 