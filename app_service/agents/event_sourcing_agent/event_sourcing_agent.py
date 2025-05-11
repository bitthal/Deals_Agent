import requests
import math
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import sys
import os
import time
import schedule
import psycopg2
import json
from uuid import uuid4

# Add parent directory to path to import logger_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from logger_config import logger


class EventSourcingAgent:
    def __init__(self):
        self.base_url = "https://api.upswap.app/api"
        self.db_params = {
            'dbname': os.getenv('DATABASE_NAME', 'deals_db'),
            'user': os.getenv('DATABASE_USER', 'deals_user'),
            'password': os.getenv('DATABASE_PASSWORD', 'deals_password'),
            'host': os.getenv('DATABASE_HOST', '172.178.68.8'),
            'port': os.getenv('DATABASE_PORT', '5432')
        }
        
    def get_db_connection(self):
        """Create a connection to the PostgreSQL database"""
        try:
            return psycopg2.connect(**self.db_params)
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return None

    def get_vendors(self) -> List[Dict]:
        """Get list of all vendors"""
        url = f"{self.base_url}/vendor/lists/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('vendors', [])
        else:
            logger.error(f"Failed to get vendors. Status code: {response.status_code}")
            return []

    def get_vendor_details(self, vendor_id: str) -> Optional[Dict]:
        """Get details of a specific vendor"""
        url = f"{self.base_url}/vendor/details/{vendor_id}/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get vendor details. Status code: {response.status_code}")
            return None

    def get_activities(self) -> List[Dict]:
        """Get list of all activities"""
        url = f"{self.base_url}/activities/lists/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get activities. Status code: {response.status_code}")
            return []

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def find_closest_activity(self, vendor_lat: float, vendor_lon: float, activities: List[Dict]) -> Optional[Dict]:
        """Find the closest activity to the vendor's location"""
        if not activities:
            return None

        closest_activity = None
        min_distance = float('inf')

        for activity in activities:
            try:
                activity_lat = float(activity['latitude'])
                activity_lon = float(activity['longitude'])
                distance = self.calculate_distance(vendor_lat, vendor_lon, activity_lat, activity_lon)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_activity = activity
            except (ValueError, KeyError) as e:
                logger.error(f"Error processing activity: {e}")
                continue

        return closest_activity

    def store_event(self, vendor_id: str, activity_id: str, activity_details: Dict) -> bool:
        """Store event in the events table"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return False

            with conn.cursor() as cur:
                # First check if an event with this activity_id already exists
                cur.execute("""
                    SELECT COUNT(*) FROM events WHERE activity_id = %s
                """, (activity_id,))
                
                if cur.fetchone()[0] > 0:
                    logger.info(f"Event with activity_id {activity_id} already exists. Skipping.")
                    return True

                # Create event details dictionary
                event_details = {
                    'title': activity_details['activity_title'],
                    'location': activity_details['location'],
                    'start_date': activity_details['start_date'],
                    'end_date': activity_details['end_date'],
                    'category': activity_details['activity_category']['actv_category'] if activity_details.get('activity_category') else None,
                    'activity_details_json': activity_details  # Include the full activity details
                }

                # Generate a new UUID for location
                location_uuid = str(uuid4())

                # Get current timestamp
                current_timestamp = datetime.now()

                # Parse coordinates from activity details
                try:
                    latitude = float(activity_details['latitude'])
                    longitude = float(activity_details['longitude'])
                except (ValueError, KeyError) as e:
                    logger.error(f"Error parsing coordinates: {e}")
                    return False

                # Prepare event data according to the schema
                event_data = {
                    'vendor_id': vendor_id,  # Keep as string
                    'location_uuid': location_uuid,  # Generate a new UUID
                    'event_trigger_point': 'local_event',  # Fixed value as per schema
                    'event_details_text': json.dumps(event_details),  # Convert dict to JSON string for database storage
                    'event_location_latitude': latitude,
                    'event_location_longitude': longitude,
                    'event_timestamp': current_timestamp,
                    'activity_id': activity_id,
                    'created_at': current_timestamp,
                    'updated_at': current_timestamp
                }

                # Insert the event
                cur.execute("""
                    INSERT INTO events (
                        vendor_id, location_uuid, event_trigger_point, 
                        event_details_text, event_location_latitude, 
                        event_location_longitude, event_timestamp, activity_id,
                        created_at, updated_at
                    ) VALUES (
                        %(vendor_id)s, %(location_uuid)s, %(event_trigger_point)s,
                        %(event_details_text)s, %(event_location_latitude)s,
                        %(event_location_longitude)s, %(event_timestamp)s, %(activity_id)s,
                        %(created_at)s, %(updated_at)s
                    )
                """, event_data)
                
                conn.commit()
                logger.info(f"Event stored successfully: {event_data}")
                return True

        except Exception as e:
            logger.error(f"Failed to store event: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def process_vendor(self, vendor: Dict) -> bool:
        """Process a single vendor"""
        try:
            vendor_id = vendor['vendor_id']
            vendor_details = self.get_vendor_details(vendor_id)
            
            if not vendor_details or not vendor_details.get('addresses'):
                logger.error(f"No addresses found for vendor {vendor_id}")
                return False

            # Get first address coordinates
            first_address = vendor_details['addresses'][0]
            vendor_lat = float(first_address['latitude'])
            vendor_lon = float(first_address['longitude'])

            # Get activities and find closest one
            activities = self.get_activities()
            closest_activity = self.find_closest_activity(vendor_lat, vendor_lon, activities)

            if not closest_activity:
                logger.error(f"No activities found near vendor {vendor_id}")
                return False

            # Store event
            success = self.store_event(
                vendor_id=vendor_id,
                activity_id=closest_activity['activity_id'],
                activity_details=closest_activity
            )

            if success:
                logger.info(f"Successfully processed vendor {vendor_id} with activity {closest_activity['activity_id']}")
            return success

        except Exception as e:
            logger.error(f"Error processing vendor {vendor.get('vendor_id', 'unknown')}: {e}")
            return False

    def run(self):
        """Main execution flow"""
        try:
            # Get all vendors
            vendors = self.get_vendors()
            if not vendors:
                logger.error("No vendors found")
                return

            # For now, process only the first vendor
            # TODO: Process all vendors in the future
            first_vendor = vendors[0]
            success = self.process_vendor(first_vendor)
            
            if success:
                logger.info("Event sourcing agent completed successfully")
            else:
                logger.error("Event sourcing agent failed")

        except Exception as e:
            logger.error(f"Event sourcing agent failed with error: {e}")

def job():
    """Job function to be scheduled"""
    logger.info("Starting scheduled event sourcing job")
    agent = EventSourcingAgent()
    agent.run()
    logger.info("Completed scheduled event sourcing job")

def run_scheduler():
    """Run the scheduler"""
    logger.info("Starting event sourcing scheduler")
    
    # Schedule the job to run every 5 minutes
    schedule.every(2).minutes.do(job)
    
    # Run the job immediately on startup
    job()
    
    # Keep the script running and execute scheduled jobs
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
            time.sleep(60)  # Wait a minute before retrying if there's an error

if __name__ == "__main__":
    run_scheduler() 