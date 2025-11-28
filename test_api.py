import requests
import json

BASE_URL = "http://localhost:5000"

# Login
login_data = {"username": "admin", "password": "admin123"}
response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
print(f"Login: {response.status_code}")

if response.status_code == 200:
    token = response.json().get('access_token')
    print(f"Token obtido: {token[:50]}...")
    
    # Get ambulantes
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/ambulantes?page=1&per_page=10", headers=headers)
    print(f"\nAmbulantes: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {len(data.get('items', []))}")
        for item in data.get('items', [])[:2]:
            print(f"  - {item['nome']}")
    else:
        print(f"Error: {response.text}")
    
    # Get produtos
    response = requests.get(f"{BASE_URL}/api/produtos?page=1&per_page=10", headers=headers)
    print(f"\nProdutos: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {len(data.get('items', []))}")
        for item in data.get('items', [])[:2]:
            print(f"  - {item['nome']}")
    else:
        print(f"Error: {response.text}")
else:
    print(f"Login failed: {response.text}")
