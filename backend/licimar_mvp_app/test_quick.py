#!/usr/bin/env python3
"""Quick test to verify all endpoints are working"""
from src.main import create_app
import json

app = create_app()

with app.app_context():
    with app.test_client() as client:
        print("\n" + "="*60)
        print("QUICK TEST - API Endpoints")
        print("="*60)
        
        # Test 1: Health check
        print("\n[TEST 1] Health Check")
        response = client.get('/api/health')
        print(f"  Status: {response.status_code}")
        assert response.status_code == 200, "Health check failed"
        print("  ✓ PASS")
        
        # Test 2: Login
        print("\n[TEST 2] Login")
        login_resp = client.post('/api/auth/login', 
            json={'username': 'admin', 'password': 'admin123'},
            content_type='application/json')
        print(f"  Status: {login_resp.status_code}")
        assert login_resp.status_code == 200, "Login failed"
        token = login_resp.get_json()['access_token']
        print("  ✓ PASS")
        
        # Test 3: Get Ambulantes
        print("\n[TEST 3] Get Ambulantes")
        response = client.get('/api/ambulantes',
            headers={'Authorization': f'Bearer {token}'})
        print(f"  Status: {response.status_code}")
        data = response.get_json()
        print(f"  Count: {len(data) if isinstance(data, list) else 'ERROR'}")
        if isinstance(data, list) and len(data) > 0:
            print(f"  First ambulante: {data[0]['nome']}")
            print(f"    - divida_acumulada: {data[0].get('divida_acumulada', 'N/A')}")
        assert response.status_code == 200, "Get ambulantes failed"
        print("  ✓ PASS")
        
        # Test 4: Get Produtos
        print("\n[TEST 4] Get Produtos")
        response = client.get('/api/produtos',
            headers={'Authorization': f'Bearer {token}'})
        print(f"  Status: {response.status_code}")
        data = response.get_json()
        print(f"  Count: {len(data) if isinstance(data, list) else 'ERROR'}")
        if isinstance(data, list) and len(data) > 0:
            print(f"  First produto: {data[0]['nome']}")
            print(f"    - peso: {data[0].get('peso', 'N/A')}")
        assert response.status_code == 200, "Get produtos failed"
        print("  ✓ PASS")
        
        # Test 5: Get Categorias
        print("\n[TEST 5] Get Categorias")
        response = client.get('/api/categorias',
            headers={'Authorization': f'Bearer {token}'})
        print(f"  Status: {response.status_code}")
        data = response.get_json()
        print(f"  Count: {len(data) if isinstance(data, list) else 'ERROR'}")
        assert response.status_code == 200, "Get categorias failed"
        print("  ✓ PASS")
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60 + "\n")
