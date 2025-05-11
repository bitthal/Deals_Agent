import requests
 
vendor_id = "6971cb91-b62b-4e5c-af83-a5baa82dfab3"
 
url = f"https://api.upswap.app/api/check-vendor/{vendor_id}/"
 
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
    'is_vendor': True,
    'vendor_id': 'e88fe995-b11b-478a-86ca-63fd047752b9'
}
"""