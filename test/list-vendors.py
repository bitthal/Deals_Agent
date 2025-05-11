import requests

url = "https://api.upswap.app/api/vendor/lists/"
 
response = requests.get(url)
 
if response.status_code == 200:
    print("Success:")
    print(response.json())
else:
    print(f"Request failed with status code: {response.status_code}")
    print("Response text:")
    print(response.text)
    
    
    
"""
Example response:-

{
  "message": "List of Vendors",
  "vendors": [
    {
      "profile_pic": "https://upswap-assets.b-cdn.net/vendor_kyc/vendor_kyc_profile_images/asset_41adb6c8-f6a0-4d4b-b371-58ca4d7c9971.webp",
      "full_name": "Rahul Jadon",
      "vendor_id": "d36fb11e-a4a6-4e2c-936b-ff296946a599",
      "user": "0aa31117-5565-4360-aaf1-05730362706e",
      "uploaded_images": [
        {
          "compressed": "https://upswap-assets.b-cdn.net/raise_an_issue_customuser/asset_8923ba2a-82ac-425a-b574-b4cacb303a3d.webp",
          "thumbnail": "https://upswap-assets.b-cdn.net/raise_an_issue_customuser/thumbnail_asset_8923ba2a-82ac-425a-b574-b4cacb303a3d.webp"
        }
      ],
      "services": [
        {
          "uuid": "edc752a1-8748-421a-ac87-765289296abe",
          "item_name": "CHAIR",
          "service_category": "Furniture",
          "item_description": "this is item description",
          "item_price": "1500.00"
        }
      ],
      "addresses": [
        {
          "uuid": "8483ec12-4c99-4050-8ffc-332f5ed8befb",
          "house_no_building_name": "meera 2a 202",
          "road_name_area_colony": "omaxe eternity vrindavan",
          "country": "India",
          "state": "Delhi",
          "city": "Central Delhi",
          "pincode": "121214",
          "latitude": "27.572680",
          "longitude": "77.650602"
        }
      ],
      "is_favorite": false,
      "average_rating": 0.0
    },
    {
      "profile_pic": "",
      "full_name": "Krishna Kumar gautam",
      "vendor_id": "463b34f1-eeb2-4a30-866c-02c5c6f8efb3",
      "user": "beedb4a5-de7f-46a8-a3b7-b6ff6dfe070e",
      "uploaded_images": [
        {
          "compressed": "https://upswap-assets.b-cdn.net/vendor_kyc/asset_60582a83-a346-4a18-adf3-ce637ab8f118.webp",
          "thumbnail": "https://upswap-assets.b-cdn.net/vendor_kyc/thumbnail_asset_60582a83-a346-4a18-adf3-ce637ab8f118.webp"
        }
      ],
      "services": [
        {
          "uuid": "67c77f76-c7c2-4c11-b869-af5dd81c2463",
          "item_name": "shoes",
          "service_category": "Others",
          "item_description": "shoes are available in kulshrestha shoes center",
          "item_price": "3000.00"
        },
        {
          "uuid": "510dc170-a809-413b-a12e-1f3bc5c02ef4",
          "item_name": "slippers",
          "service_category": "Others",
          "item_description": "slippers are available in kulshrestha shoes center",
          "item_price": "1000.00"
        },
        {
          "uuid": "77a7d9e0-1a41-4969-8b21-b21f562cbb12",
          "item_name": "cloths",
          "service_category": "Clothing",
          "item_description": "for all male and female",
          "item_price": "2000.00"
        }
      ],
      "addresses": [
        {
          "uuid": "40a29fd8-1ba4-4cdc-9239-ada6c6918751",
          "house_no_building_name": "kulshrestha shoes center",
          "road_name_area_colony": "mathura vrindavan road",
          "country": "India",
          "state": "Uttar Pradesh",
          "city": "Mathura",
          "pincode": "281003",
          "latitude": "27.524823",
          "longitude": "77.674384"
        }
      ],
      "is_favorite": false,
      "average_rating": 0.0
    }
  ]
}
"""