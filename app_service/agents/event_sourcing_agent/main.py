import psycopg2
from geopy.geocoders import Nominatim
import requests
from geopy.distance import geodesic
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT', '5432')
}

# Second database connection parameters
DB_PARAMS_2 = {
    'dbname': os.getenv('DB_NAME_2'),
    'user': os.getenv('DB_USER_2'),
    'password': os.getenv('DB_PASSWORD_2'),
    'host': os.getenv('DB_HOST_2'),
    'port': os.getenv('DB_PORT_2', '5432')
}

def get_db_connection():
    """Create a connection to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def get_db_hackathon():
    """Create a connection to the second PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_PARAMS_2)
        return conn
    except Exception as e:
        print(f"Error connecting to second database: {e}")
        return None

def get_vendor_locations():
    """Retrieve vendor locations from the database"""
    conn = get_db_connection()
    if not conn:
        print("Failed to establish database connection")
        return []
    
    try:
        with conn.cursor() as cur:
            # First, let's check the table structure
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'main_customuser'
            """)
            columns = cur.fetchall()
            print(f"Table structure: {columns}")
            
            # Now get the vendor locations
            cur.execute("""
                SELECT id, latitude, longitude 
                FROM main_customuser 
                WHERE latitude IS NOT NULL 
                AND longitude IS NOT NULL
            """)
            locations = cur.fetchall()
            print(f"Found {len(locations)} vendor locations with valid coordinates")
            for loc in locations:
                print(f"Vendor {loc[0]}: lat={loc[1]}, lon={loc[2]}")
            return locations
    except Exception as e:
        print(f"Error fetching vendor locations: {e}")
        return []
    finally:
        conn.close()

def insert_event_into_hackathon_db(event):
    """Insert event details into the hackathon database, checking for existence first."""
    conn = get_db_hackathon()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            # Check if the event already exists by activity_id
            cur.execute("SELECT 1 FROM events WHERE activity_id = %s", (event['activity_id'],))
            if cur.fetchone():
                print(f"Event with activity_id {event['activity_id']} already exists.")
                return False
            
            # Fetch activity details from the API
            try:
                activity_details_url = f"https://api.upswap.app/api/activities/details/{event['activity_id']}/"
                response = requests.get(activity_details_url, timeout=10)
                response.raise_for_status()
                activity_details = response.json()
            except Exception as e:
                print(f"Error fetching activity details: {e}")
                activity_details = None
            
            # Create event details JSON
            event_details = {
                'title': event['activity_title'],
                'location': event['location'],
                'start_date': event['start_date'],
                'end_date': event['end_date'],
                'category': event['activity_category']['actv_category'] if event['activity_category'] else None,
                'activity_details_json': activity_details  # Include the full activity details
            }
            
            # Convert dictionary to JSON string
            event_details_json = json.dumps(event_details)
            
            # Insert the event into the events table
            cur.execute("""
                INSERT INTO events (activity_id, event_trigger_point, event_details_text, event_location_latitude, event_location_longitude)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                event['activity_id'],
                "local_event",
                event_details_json,
                event['latitude'],
                event['longitude']
            ))
            conn.commit()
            print(f"Inserted event with activity_id {event['activity_id']} into the hackathon database.")
            return True
    except Exception as e:
        print(f"Error inserting event into hackathon database: {e}")
        return False
    finally:
        conn.close()


def get_address_from_coordinates(latitude, longitude):
    """Get address from coordinates using Nominatim"""
    geolocator = Nominatim(user_agent="vendor_events_finder")
    try:
        location = geolocator.reverse(f"{latitude}, {longitude}")
        return location.address if location else "Address not found"
    except Exception as e:
        print(f"Error getting address: {e}")
        return "Address not found"

def find_nearby_events(latitude, longitude, radius_miles=3):
    """
    Find events near the given coordinates using a hypothetical events API
    You'll need to replace this with an actual events API of your choice
    """
    # This is a placeholder - replace with actual API endpoint and parameters
    api_key = os.getenv('EVENTS_API_KEY')
    if not api_key:
        print("Events API key not found")
        return []

    try:
        # Example using a hypothetical events API
        # Replace this with your chosen events API
        url = f"https://api.events.example.com/search"
        params = {
            'lat': latitude,
            'lon': longitude,
            'radius': radius_miles,
            'api_key': api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error finding nearby events: {e}")
        return []

def main():
    # Get vendor locations from both databases
    vendor_locations = get_vendor_locations()
    
    for vendor_id, latitude, longitude in vendor_locations:
        print(f"\nProcessing vendor ID: {vendor_id}")
        print(f"Latitude: {latitude}, Longitude: {longitude}")

        # # Get address from coordinates
        # address = get_address_from_coordinates(latitude, longitude)
        # print(f"Vendor Address: {address}")
        
        # # Find nearby events
        # events = find_nearby_events(latitude, longitude)
        # print(f"Found {len(events)} events nearby")
        
        # # Process events (customize based on your events API response format)
        # for event in events:
        #     print(f"Event: {event.get('name', 'Unknown')}")

if __name__ == "__main__":
    main() 