import requests
 
vendor_id = "da3f7067-baf9-4198-badb-d8927a42ee36"
 
url = f"http://127.0.0.1:8000/api/check-vendor/{vendor_id}/"
 
response = requests.get(url)
 
if response.status_code == 200:
    print("Success:")
    print(response.json())
else:
    print(f"Request failed with status code: {response.status_code}")
    print("Response text:")
    print(response.text)