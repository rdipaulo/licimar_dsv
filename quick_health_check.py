#!/usr/bin/env python3
"""Quick health check"""
import requests

try:
    response = requests.get('http://127.0.0.1:5000/api/health', timeout=5)
    print(f"Status: {response.status_code}")
    print(response.json())
except Exception as e:
    print(f"Error: {e}")
