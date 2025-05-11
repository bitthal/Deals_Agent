import os
import time
import logging
import schedule
from datetime import datetime
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from logger_config import logger
from get_events_from_upswap import monitor_vendor_locations
from main import get_db_hackathon

# Load environment variables
load_dotenv()

def job():
    """Main job function that runs every 1 minute"""
    try:
        logger.info("Starting scheduled event sourcing job")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Job started at: {current_time}")

        # Only collect events from Upswap
        logger.info("Collecting event from Upswap")
        monitor_vendor_locations()

        logger.info("Event sourcing job completed successfully")
    except Exception as e:
        logger.error(f"Error in scheduled job: {str(e)}")

def main():
    """Main function to run the scheduler"""
    logger.info("Starting event sourcing scheduler")
    
    # Schedule the job to run every 1 minute
    schedule.every(1).minutes.do(job)
    
    # Run the job immediately on startup
    job()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main() 