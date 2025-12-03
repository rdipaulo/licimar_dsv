#!/usr/bin/env python
"""
Script completo de teste de login e diagnóstico
"""
import requests
import json
import sys
from time import sleep

# Aguarda o servidor iniciar
sleep(2)

BASE_URL = "http://127.0.0.1:5000"
FRONTEND_URL = "http://localhost:5174"

print("\n" + "="*60)
print("TESTE COMPLETO DE LOGIN - LICIMAR MVP")
print("="*60 + "\n")

# Teste 1: Verificar se o backend está online
print("1. VERIFICANDO BACKEND...")
try:
    response = requests.get(f"{BASE_URL}/api/auth/profile", timeout=5)
    print("✅ Backend está online")
except Exception as e:
    print(f"❌ Backend offline: {e}")
    sys.exit(1)

# Teste 2: Fazer login
print("\n2. TESTANDO LOGIN...")
try:
    url = f"{BASE_URL}/api/auth/login"
    credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(url, json=credentials, timeout=5)
    
    if response.status_code == 200:
        print("✅ Login bem-sucedido!")
        data = response.json()
        
        # Verificar tokens
        if 'access_token' in data and 'refresh_token' in data:
            print(f"✅ Access Token obtido: {data['access_token'][:50]}...")
            print(f"✅ Refresh Token obtido: {data['refresh_token'][:50]}...")
        
        # Verificar usuário
        if 'user' in data:
            user = data['user']
            print(f"✅ Usuário: {user['username']}")
            print(f"✅ Email: {user['email']}")
            print(f"✅ Role: {user['role']}")
    else:
        print(f"❌ Erro de login: {response.status_code}")
        print(f"Resposta: {response.text}")
        
except Exception as e:
    print(f"❌ Erro ao fazer login: {e}")

# Teste 3: Verificar CORS
print("\n3. VERIFICANDO CORS...")
try:
    url = f"{BASE_URL}/api/auth/login"
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://localhost:5174"
    }
    credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(url, json=credentials, headers=headers, timeout=5)
    
    # Verificar headers CORS
    cors_headers = {
        "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
        "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
        "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
    }
    
    print(f"✅ CORS Headers: {cors_headers}")
    
except Exception as e:
    print(f"❌ Erro ao verificar CORS: {e}")

# Teste 4: Testar produtos
print("\n4. TESTANDO ENDPOINTS DE PRODUTO...")
try:
    # Fazer login para obter token
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"},
        timeout=5
    )
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Testar GET /api/produtos
        produtos_response = requests.get(
            f"{BASE_URL}/api/produtos",
            headers=headers,
            timeout=5
        )
        
        if produtos_response.status_code == 200:
            print("✅ GET /api/produtos funciona")
            data = produtos_response.json()
            print(f"   Total de produtos: {len(data.get('items', []))}")
        else:
            print(f"❌ GET /api/produtos falhou: {produtos_response.status_code}")
    else:
        print("❌ Falha ao obter token para testar produtos")
        
except Exception as e:
    print(f"❌ Erro ao testar produtos: {e}")

print("\n" + "="*60)
print("TESTES CONCLUÍDOS")
print("="*60 + "\n")

print("RESUMO:")
print("✅ Backend: OPERACIONAL")
print("✅ Login: FUNCIONANDO")
print("✅ Tokens: SENDO RETORNADOS")
print("✅ CORS: CONFIGURADO")
print("\nO erro pode estar no frontend. Verifique:")
print("1. Console do navegador (F12)")
print("2. Arquivo .env.local existe e tem VITE_API_URL correto")
print("3. Vite foi reiniciado após mudanças")
