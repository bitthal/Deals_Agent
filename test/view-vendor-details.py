import requests

url = "https://api.upswap.app/api/vendor/details/d36fb11e-a4a6-4e2c-936b-ff296946a599/"

response = requests.get(url)

if response.status_code == 200:
    print("Success:")
    print(response.json())
else:
    print(f"Request failed with status code: {response.status_code}")
    print("Response text:")
    print(response.text)



"""
example response:-

{
    'vendor_id': 'd36fb11e-a4a6-4e2c-936b-ff296946a599',
    'profile_pic': 'https://upswap-assets.b-cdn.net/vendor_kyc/vendor_kyc_profile_images/asset_41adb6c8-f6a0-4d4b-b371-58ca4d7c9971.webp',
    'user': '0aa31117-5565-4360-aaf1-05730362706e',
    'full_name': 'Lalit Singh',
    'phone_number': '9193045575',
    'business_email_id': 'rahuljadon99@gmail.com',
    'business_establishment_year': 2020,
    'business_description': 'this is business description',
    'uploaded_business_documents': [
        'https://upswap-assets.b-cdn.net/vendor_kyc/vendor_kyc_documents/asset_bd4aaa59-3e85-4d0a-85a6-7033472dd783.webp'
    ],
    'uploaded_images': [
        {
            'compressed': 'https://upswap-assets.b-cdn.net/raise_an_issue_customuser/asset_8923ba2a-82ac-425a-b574-b4cacb303a3d.webp',
            'thumbnail': 'https://upswap-assets.b-cdn.net/raise_an_issue_customuser/thumbnail_asset_8923ba2a-82ac-425a-b574-b4cacb303a3d.webp'
        }
    ],
    'same_as_personal_phone_number': True,
    'same_as_personal_email_id': True,
    'addresses': [
        {
            'uuid': '8483ec12-4c99-4050-8ffc-332f5ed8befb',
            'house_no_building_name': 'meera 2a 202',
            'road_name_area_colony': 'omaxe eternity vrindavan',
            'country': 'India',
            'state': 'Delhi',
            'city': 'Central Delhi',
            'pincode': '121214',
            'latitude': '27.572680',
            'longitude': '77.650602'
        }
    ],
    'country_code': 'IN',
    'dial_code': '+91',
    'bank_account_number': '147852147852',
    'retype_bank_account_number': '147852147852',
    'bank_name': 'bank of baroda',
    'ifsc_code': 'BARB0BARSAN',
    'services': [
        {
            'uuid': 'edc752a1-8748-421a-ac87-765289296abe',
            'item_name': 'CHAIR',
            'service_category': 'Furniture',
            'item_description': 'this is item description',
            'item_price': '1500.00'
        }
    ],
    'business_hours': [
        {'day': 'Sunday', 'time': '11:00 AM - 7:00 PM'},
        {'day': 'Monday', 'time': '10:00 AM - 8:00 PM'},
        {'day': 'Tuesday', 'time': '10:00 AM - 8:00 PM'},
        {'day': 'Wednesday', 'time': '10:00 AM - 8:00 PM'},
        {'day': 'Thursday', 'time': '10:00 AM - 8:00 PM'},
        {'day': 'Friday', 'time': '10:00 AM - 8:00 PM'},
        {'day': 'Saturday', 'time': '10:00 AM - 8:00 PM'}
    ],
    'is_approved': True,
    'average_rating': 0.0
}
"""