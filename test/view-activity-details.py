import requests
import json

BASE_URL = "https://api.upswap.app/api/activities/details/"
ACTIVITY_ID = "4cb3a135-3741-48fb-86dd-eac0803de890"
API_URL = f"{BASE_URL}{ACTIVITY_ID}/"

try:
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    print("Success:")
    print(json.dumps(data, indent=4))

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
    if hasattr(response, 'status_code'):
        print(f"Status code: {response.status_code}")
    # if response is not None: print(f"Response content: {response.text}")

except requests.exceptions.Timeout:
    print("The request timed out.")

except requests.exceptions.ConnectionError:
    print("Failed to connect to the server. Check your network connection or the API URL.")

except json.JSONDecodeError:
    print("Error: Could not decode JSON response.")
    # if response is not None: print(f"Response content: {response.text}")

except requests.exceptions.RequestException as req_err:
    print(f"An unexpected error occurred: {req_err}")




"""
Example response:-

{
    "activity_id": "4cb3a135-3741-48fb-86dd-eac0803de890",
    "user_id": "6971cb91-b62b-4e5c-af83-a5baa82dfab3",
    "activity_title": "one test",
    "activity_description": "desc",
    "activity_category": {
        "actv_category": "Cultural Exchanges"
    },
    "uploaded_images": [],
    "user_participation": true,
    "maximum_participants": 2,
    "start_date": "2025-05-05",
    "end_date": "2025-05-05",
    "start_time": "15:35:19.731004",
    "end_time": "17:35:00",
    "created_at": "2025-05-05T15:35:19.731404Z",
    "created_by": "krishiv22",
    "set_current_datetime": true,
    "infinite_time": false,
    "location": "Delhi, India",
    "latitude": "28.704059",
    "longitude": "77.102490"
}
"""