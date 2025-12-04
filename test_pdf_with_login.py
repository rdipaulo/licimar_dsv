#!/usr/bin/env python3
"""
Test PDF endpoint - with login
"""
import requests

base_url = "http://127.0.0.1:5000"

print("[TEST] 1. Fazendo login...")
login_response = requests.post(f"{base_url}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})

if login_response.status_code != 200:
    print(f"❌ Erro no login: {login_response.text}")
    exit(1)

token = login_response.json().get("access_token")
print(f"✅ Login bem-sucedido! Token: {token[:20]}...")

print("\n[TEST] 2. Testando endpoint de PDF...")
headers = {"Authorization": f"Bearer {token}"}
pdf_response = requests.get(f"{base_url}/api/pedidos/1/imprimir", headers=headers)

print(f"Status: {pdf_response.status_code}")
print(f"Content-Type: {pdf_response.headers.get('Content-Type')}")
print(f"Content-Length: {pdf_response.headers.get('Content-Length')}")

if pdf_response.status_code == 200:
    with open('test_pdf_output.pdf', 'wb') as f:
        f.write(pdf_response.content)
    print(f"✅ PDF gerado com sucesso! Tamanho: {len(pdf_response.content)} bytes")
else:
    print(f"❌ Erro! Response: {pdf_response.text}")
