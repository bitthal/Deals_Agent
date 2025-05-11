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