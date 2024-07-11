import requests

url = "https://localhost:8000/profile/1/"
data = {"displayname": "TestUser1"}
response = requests.put(url, json=data, verify=False)

print(response.status_code)

# Check if the response status code indicates success (200-299)
if response.ok:
    # Ensure the response content type is JSON before decoding
    if 'application/json' in response.headers.get('Content-Type', ''):
        try:
            print(response.json())
        except ValueError as e:
            print("Response content is not valid JSON:", e)
    else:
        print("Response content type is not JSON:", response.headers.get('Content-Type'))
else:
    print("Request failed with status code:", response.status_code)
