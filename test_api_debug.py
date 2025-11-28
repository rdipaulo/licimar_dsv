import requests
import json

BASE_URL = "http://localhost:5000"

# Login
login_data = {"username": "admin", "password": "admin123"}
response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
token = response.json().get('access_token')

headers = {"Authorization": f"Bearer {token}"}

# Test ambulantes with debug
print("Testing ambulantes endpoint...")
response = requests.get(f"{BASE_URL}/api/ambulantes?page=1&per_page=20", headers=headers)
print(f"Status: {response.status_code}")
data = response.json()
print(f"Response: {json.dumps(data, indent=2)}")

# Try without pagination
print("\n\nTesting ambulantes without pagination params...")
response = requests.get(f"{BASE_URL}/api/ambulantes", headers=headers)
print(f"Status: {response.status_code}")
data = response.json()
print(f"Items count: {len(data.get('items', []))}")
if data.get('items'):
    print(f"First item: {data['items'][0]}")
