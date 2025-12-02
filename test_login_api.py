#!/usr/bin/env python3
"""Testar login na API"""
import requests
import json
import time

time.sleep(3)  # Aguarda backend iniciar

url = "http://127.0.0.1:5000/api/auth/login"
payload = {
    "username": "admin",
    "password": "admin123"
}

try:
    response = requests.post(url, json=payload, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Erro: {e}")
