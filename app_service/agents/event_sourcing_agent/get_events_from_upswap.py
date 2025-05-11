import time
from main import get_vendor_locations, insert_event_into_hackathon_db
import requests
from decimal import Decimal
import logging
from logger_config import logger

def find_matching_events(vendor_latitude, vendor_longitude, events):
    """Find events that match the vendor's latitude and longitude."""
    matching_events = []
    
    # Validate vendor coordinates
    if vendor_latitude is None or vendor_longitude is None:
        logger.warning(f"Invalid vendor coordinates - latitude: {vendor_latitude}, longitude: {vendor_longitude}")
        return matching_events
    
    logger.info(f"Processing vendor coordinates - latitude: {vendor_latitude}, longitude: {vendor_longitude}")
    
    # Convert vendor coordinates to Decimal
    try:
        vendor_lat = Decimal(str(vendor_latitude))
        vendor_lon = Decimal(str(vendor_longitude))
        logger.info(f"Converted vendor coordinates to Decimal - lat: {vendor_lat}, lon: {vendor_lon}")
    except (ValueError, TypeError) as e:
        logger.warning(f"Could not convert vendor coordinates: {e}")
        return matching_events
    
    # Process only the first matching event
    for event in events:
        try:
            logger.info(f"Processing event: {event.get('activity_title', 'Unknown')}")
            event_lat = Decimal(str(event['latitude']))
            event_lon = Decimal(str(event['longitude']))
            logger.info(f"Event coordinates - lat: {event_lat}, lon: {event_lon}")
            
            # Using a small tolerance for decimal comparison
            tolerance = Decimal('0.000001')
            if (abs(event_lat - vendor_lat) < tolerance and 
                abs(event_lon - vendor_lon) < tolerance):
                logger.info(f"Found matching event: {event['activity_title']}")
                logger.info(f"Event details: {event}")
                insert_event_into_hackathon_db(event)
                matching_events.append(event)
                # Return after finding the first match
                return matching_events
            else:
                logger.info(f"Event coordinates do not match vendor location")
                
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not process event coordinates: {e}")
            continue
    
    return matching_events

def get_upswap_events():
    """Fetch events from Upswap API"""
    try:
        logger.info("Fetching events from Upswap API...")
        response = requests.get("https://api.upswap.app/api/activities/lists/")
        response.raise_for_status()
        events = response.json()
        logger.info(f"Received {len(events)} events from Upswap")
        if events:
            logger.info(f"First event details: {events[0]}")
        # Return only the first event
        return [events[0]] if events else []
    except Exception as e:
        logger.error(f"Error fetching events from Upswap: {e}")
        return []

def monitor_vendor_locations():
    """Process vendor locations and find matching events"""
    try:
        # Get vendor locations
        logger.info("Fetching vendor locations...")
        vendor_locations = get_vendor_locations()
        if not vendor_locations:
            logger.warning("No vendor locations found")
            return
        
        logger.info(f"Found {len(vendor_locations)} vendor locations")
        
        # Get single event from Upswap
        events_data = get_upswap_events()
        if not events_data:
            logger.warning("No events data received from Upswap")
            return

        # Process only the first vendor
        vendor_id, latitude, longitude = vendor_locations[0]
        logger.info(f"Processing vendor ID: {vendor_id}")
        logger.info(f"Vendor coordinates - latitude: {latitude}, longitude: {longitude}")
        
        # Find matching events for the vendor's location
        matching_events = find_matching_events(latitude, longitude, events_data)
        logger.info(f"Found {len(matching_events)} matching events for vendor ID {vendor_id}")

    except Exception as e:
        logger.error(f"Error in monitor_vendor_locations: {e}")
        raise

if __name__ == "__main__":
    print("Starting vendor location monitoring...")
    monitor_vendor_locations()
