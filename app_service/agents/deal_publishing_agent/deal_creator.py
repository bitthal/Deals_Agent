import os
import time
import requests
import schedule
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from logger_config import logger

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'deals_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

# API configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.upswap.app/api')

# Database connection
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

def get_accepted_suggestions():
    """Fetch deal suggestions that have been accepted by vendors."""
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT * FROM deal_suggestions 
                WHERE vendor_feedback = 'accepted' 
                AND status != 'posted'
            """)
            result = conn.execute(query)
            return result.fetchall()
    except Exception as e:
        logger.error(f"Error fetching accepted suggestions: {str(e)}")
        return []

def update_suggestion_status(suggestion_id):
    """Update the status of a processed deal suggestion."""
    try:
        with engine.connect() as conn:
            query = text("""
                UPDATE deal_suggestions 
                SET status = 'posted', 
                    updated_at = :updated_at 
                WHERE id = :id
            """)
            conn.execute(query, {
                "id": suggestion_id,
                "updated_at": datetime.utcnow()
            })
            conn.commit()
    except Exception as e:
        logger.error(f"Error updating suggestion status: {str(e)}")

def create_deal(suggestion):
    """Create a deal using the API based on the suggestion data."""
    try:
        url = f"{API_BASE_URL}/create-deal/hackathon/"
        
        # Prepare the payload from suggestion data
        payload = {
            "deal_title": suggestion.deal_title,
            "deal_description": suggestion.deal_description,
            "select_service": suggestion.service_category,
            "uploaded_images": suggestion.images,
            "start_date": suggestion.start_date.strftime("%Y-%m-%d"),
            "end_date": suggestion.end_date.strftime("%Y-%m-%d"),
            "start_time": suggestion.start_time.strftime("%H:%M:%S"),
            "end_time": suggestion.end_time.strftime("%H:%M:%S"),
            "start_now": "true",
            "actual_price": str(suggestion.actual_price),
            "deal_price": str(suggestion.deal_price),
            "available_deals": str(suggestion.available_deals),
            "location_house_no": suggestion.location_house_no,
            "location_road_name": suggestion.location_road_name,
            "location_country": suggestion.location_country,
            "location_state": suggestion.location_state,
            "location_city": suggestion.location_city,
            "location_pincode": suggestion.location_pincode,
            "vendor_kyc": suggestion.vendor_kyc,
            "latitude": suggestion.latitude,
            "longitude": suggestion.longitude
        }

        response = requests.post(url, json=payload)
        
        if response.status_code in [200, 201]:
            logger.info(f"Successfully created deal for suggestion {suggestion.id}")
            update_suggestion_status(suggestion.id)
            return True
        else:
            logger.error(f"Failed to create deal for suggestion {suggestion.id}. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating deal: {str(e)}")
        return False

def process_suggestions():
    """Main function to process accepted suggestions."""
    logger.info("Starting to process deal suggestions...")
    suggestions = get_accepted_suggestions()
    
    for suggestion in suggestions:
        logger.info(f"Processing suggestion ID: {suggestion.id}")
        if create_deal(suggestion):
            logger.info(f"Successfully processed suggestion {suggestion.id}")
        else:
            logger.error(f"Failed to process suggestion {suggestion.id}")

def main():
    """Main function to run the scheduler."""
    logger.info("Starting Deal Creation Agent...")
    
    # Schedule the job to run every 5 minutes
    schedule.every(5).minutes.do(process_suggestions)
    
    # Run immediately on startup
    process_suggestions()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main() 