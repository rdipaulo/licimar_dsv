#!/usr/bin/env python3
"""Debug response format"""
from src.main import create_app
import json

app = create_app()

with app.app_context():
    with app.test_client() as client:
        # Login
        login_resp = client.post('/api/auth/login', 
            json={'username': 'admin', 'password': 'admin123'},
            content_type='application/json')
        token = login_resp.get_json()['access_token']
        
        # Get ambulantes
        response = client.get('/api/ambulantes',
            headers={'Authorization': f'Bearer {token}'})
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.content_type}")
        print(f"Data Type: {type(response.data)}")
        print(f"Raw Data: {response.data[:500]}")
        print(f"\nParsed JSON:")
        print(json.dumps(response.get_json(), indent=2)[:1000])
