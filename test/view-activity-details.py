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