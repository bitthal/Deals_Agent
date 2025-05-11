import requests

url = "https://api.upswap.app/api/create-deal/hackathon/"

payload = {
    "deal_title": "Weekend Bakery Special",
    "deal_description": "Delicious cakes, pastries, and fresh bread at half price!",
    "select_service": "Food & Dining", # Changed from "Consulting"
    "uploaded_images": [{
        "thumbnail": "https://upswap-assets.b-cdn.net/create_deal/thumbnail_asset_abcdef12-3456-7890-abcd-ef1234567890.webp", # New dummy image URL
        "compressed": "https://upswap-assets.b-cdn.net/create_deal/asset_abcdef12-3456-7890-abcd-ef1234567890.webp" # New dummy image URL
    }],
    "start_date": "2025-11-22", # Changed date
    "end_date": "2025-11-23",   # Changed date
    "start_time": "09:00:00", # Changed time
    "end_time": "19:00:00",   # Changed time
    "start_now": "true",      # Changed to true
    "actual_price": "600",    # Changed price
    "deal_price": "300",      # Changed price
    "available_deals": "25",  # Changed quantity
    "location_house_no": "Shop No. 7, Sunrise Complex", # New location details
    "location_road_name": "MG Road",
    "location_country": "India",
    "location_state": "Karnataka", # Changed state
    "location_city": "Bangalore",   # Changed city
    "location_pincode": "560001",  # Changed pincode
    "vendor_kyc": "e88fe995-b11b-478a-86ca-63fd047752b9", # Kept the same as requested
    "latitude": 12.9716,  # Approx latitude for Bangalore
    "longitude": 77.5946 # Approx longitude for Bangalore
}

response = requests.post(url, json=payload)

# It's good practice to check the status code before trying to parse JSON
if response.status_code == 200 or response.status_code == 201: # Or whatever success codes are expected
    print("Success:")
    print(response.json())
else:
    print(f"Request failed with status code: {response.status_code}")
    print("Response text:")
    print(response.text)





"""
Example response:-

{
    'message': 'Deal created successfully!',
    'data': {
        'deal_uuid': 'ac703267-a5cb-458a-b6cc-8ea252f176ce',
        'deal_title': 'Weekend Bakery Special',
        'deal_description': 'Delicious cakes, pastries, and fresh bread at half price!',
        'select_service': 'Food & Dining',
        'uploaded_images': [
            {
                'thumbnail': 'https://upswap-assets.b-cdn.net/create_deal/thumbnail_asset_abcdef12-3456-7890-abcd-ef1234567890.webp',
                'compressed': 'https://upswap-assets.b-cdn.net/create_deal/asset_abcdef12-3456-7890-abcd-ef1234567890.webp'
            }
        ],
        'start_date': '2025-05-11',
        'end_date': '2025-11-23',
        'start_time': '16:11:20',
        'end_time': '19:00:00',
        'start_now': True,
        'buy_now': True,
        'actual_price': '600.00',
        'deal_price': '300.00',
        'available_deals': 25,
        'location_house_no': 'Shop No. 7, Sunrise Complex',
        'location_road_name': 'MG Road',
        'location_country': 'India',
        'location_state': 'Karnataka',
        'location_city': 'Bangalore',
        'location_pincode': '560001',
        'vendor_kyc': 'e88fe995-b11b-478a-86ca-63fd047752b9',
        'vendor_name': 'Krishiv Lawaniya',
        'vendor_uuid': 'e88fe995-b11b-478a-86ca-63fd047752b9',
        'vendor_email': 'krishivlawaniya@gmail.com',
        'vendor_number': '9259573845',
        'discount_percentage': 50.0,
        'latitude': '12.971600',
        'longitude': '77.594600',
        'deal_post_time': '2025-05-11 16:11:20'
    }
}
"""