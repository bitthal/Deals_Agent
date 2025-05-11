import requests

url = "https://api.upswap.app/api/activities/lists/"

response = requests.get(url)

print(response.json())



"""
Example response:-

[
  {
    "activity_id": "da731c2c-cbcf-4f84-882a-76d9c12a47a7",
    "user_id": "18537256-94d3-4d39-945f-35a34de80697",
    "activity_title": "The Shri Banke Bihari Temple in Vrindavan, Mathura",
    "uploaded_images": [
      "https://upswap-assets.b-cdn.net/create_deal/thumbnail_asset_d423b11a-e168-41b5-ae74-f597a68a491e.webp"
    ],
    "activity_category": {
      "actv_category": "Social Gatherings"
    },
    "created_by": "lalitsingh0984",
    "user_participation": true,
    "infinite_time": true,
    "start_date": "2025-04-29",
    "start_time": "13:37:05.746043",
    "end_date": "3023-08-31",
    "end_time": "13:37:05.746046",
    "latitude": "27.574719",
    "longitude": "77.652463",
    "location": "Lat: 27.5747, Lng: 77.6525"
  },
  {
    "activity_id": "74734abc-f7ba-4149-badf-f03d851cea0d",
    "user_id": "6971cb91-b62b-4e5c-af83-a5baa82dfab3",
    "activity_title": "Krishiv Activity",
    "uploaded_images": [
      "https://upswap-assets.b-cdn.net/activity/thumbnail_asset_ee937b77-f21d-42be-b151-b7306c98d197.webp"
    ],
    "activity_category": {
      "actv_category": "Others"
    },
    "created_by": "krishiv22",
    "user_participation": true,
    "infinite_time": true,
    "start_date": "2025-05-06",
    "start_time": "07:15:10",
    "end_date": "2125-05-06",
    "end_time": "07:15:00",
    "latitude": "27.565009",
    "longitude": "77.659339",
    "location": ", Vrindavan, Uttar Pradesh, India, 281121"
  }
]


"""