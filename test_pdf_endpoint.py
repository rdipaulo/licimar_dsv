#!/usr/bin/env python3
"""
Test PDF endpoint
"""
import requests
import sys

# Adicionar ao path
sys.path.insert(0, 'backend/licimar_mvp_app')

# Token de teste (válido por 24h)
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoiYWRtaW4iLCJpYXQiOjE3MzM0OTM3ODMsImV4cCI6MTczMzU4MDE4M30.5FzzFKG3kR8Pq6Vb7vWkWXzYNegwMC9TwFvgF3s4qEU"

url = "http://127.0.0.1:5000/api/pedidos/1/imprimir"
headers = {
    "Authorization": f"Bearer {token}"
}

print(f"[TEST] Testando endpoint: {url}")
print(f"[TEST] Enviando request com token...")

try:
    response = requests.get(url, headers=headers)
    print(f"[TEST] Status Code: {response.status_code}")
    print(f"[TEST] Content-Type: {response.headers.get('Content-Type')}")
    print(f"[TEST] Content-Length: {response.headers.get('Content-Length')}")
    
    if response.status_code == 200:
        with open('test_pdf_output.pdf', 'wb') as f:
            f.write(response.content)
        print(f"[TEST] ✅ PDF gerado com sucesso! Tamanho: {len(response.content)} bytes")
        print(f"[TEST] Arquivo salvo em: test_pdf_output.pdf")
    else:
        print(f"[TEST] ❌ Erro! Resposta: {response.text}")
        
except Exception as e:
    print(f"[TEST] ❌ Erro ao fazer request: {e}")
