import requests
import json

BASE_URL = "http://localhost:5000"

# Try to login
payload = {
    "username": "admin",
    "password": "admin"
}

response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200:
    data = response.json()
    print(f"\nAccess Token: {data.get('access_token', 'N/A')[:50]}...")
    print(f"User: {data.get('user', {})}")
