#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug teste saída com gelo decimal"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

try:
    # Login
    resp = requests.post(f"{BASE_URL}/api/auth/login", 
        json={"username": "admin", "password": "admin123"})
    if resp.status_code != 200:
        print(f"Login falhou: {resp.status_code} - {resp.text}")
        exit(1)
    
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login OK")

    # Get clientes
    resp = requests.get(f"{BASE_URL}/api/clientes", headers=headers)
    clientes_data = resp.json()
    if 'items' in clientes_data:
        cliente_id = clientes_data['items'][0]['id']
    else:
        cliente_id = clientes_data[0]['id']
    print(f"✅ Cliente ID: {cliente_id}")

    # Get produtos
    resp = requests.get(f"{BASE_URL}/api/produtos", headers=headers)
    produtos_data = resp.json()
    if 'items' in produtos_data:
        produtos = produtos_data['items']
    else:
        produtos = produtos_data
    
    gelo = next((p for p in produtos if p['nome'] == 'Gelo Seco (kg)'), None)
    if not gelo:
        print(f"❌ Gelo não encontrado")
        exit(1)
    print(f"✅ Gelo ID: {gelo['id']}, preco={gelo['preco']}")
    print()

    # Create saída with decimal
    saida_data = {
        'cliente_id': cliente_id,
        'itens_saida': [
            {
                'produto_id': gelo['id'],
                'quantidade_saida': 2.5,
                'preco': gelo['preco']
            }
        ]
    }

    print("Enviando saída com gelo=2.5:")
    print(json.dumps(saida_data, indent=2))
    print()

    resp = requests.post(f"{BASE_URL}/api/pedidos/saida", 
        json=saida_data, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    
    if resp.status_code != 201:
        print("\n⚠️ Erro ao criar saída!")
        print(f"Full response: {resp.text}")
    else:
        print("\n✅ Saída criada com sucesso!")
        
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()
