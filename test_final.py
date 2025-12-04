#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Teste dos 3 problemas - simples"""
import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

try:
    # LOGIN
    resp = requests.post(f"{BASE_URL}/api/auth/login", 
        json={"username": "admin", "password": "admin123"})
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("[OK] Login")

    # GET CLIENTES
    resp = requests.get(f"{BASE_URL}/api/clientes", headers=headers)
    clientes = resp.json()['items']
    cliente_id = clientes[0]['id']

    # GET PRODUTOS
    resp = requests.get(f"{BASE_URL}/api/produtos", headers=headers)
    produtos = resp.json()['items']
    
    gelo = next((p for p in produtos if p['nome'] == 'Gelo Seco (kg)'), None)
    
    print("[OK] Gelo: nao_devolve={}".format(gelo['nao_devolve']))

    print("\nPROBLEMA 1: GELO COM VALOR DECIMAL")
    
    saida_data = {
        'cliente_id': cliente_id,
        'itens_saida': [
            {'produto_id': gelo['id'], 'quantidade_saida': 2.5}
        ]
    }
    
    resp = requests.post(f"{BASE_URL}/api/pedidos/saida", 
        json=saida_data, headers=headers)
    
    if resp.status_code == 201:
        pedido = resp.json()['pedido']
        print("[OK] Status 201 - Saida: {} kg".format(pedido['itens'][0]['quantidade_saida']))
        problema1 = True
        pedido_id = pedido['id']
    else:
        print("[ERRO] Status {}".format(resp.status_code))
        problema1 = False

    print("\nPROBLEMA 2: PDF/PRINT")
    
    if problema1:
        try:
            resp = requests.get(f"{BASE_URL}/api/pedidos/{pedido_id}/imprimir", 
                headers=headers, timeout=10)
            
            if resp.status_code == 200:
                if b'%PDF' in resp.content[:10]:
                    print("[OK] PDF gerado: {} bytes".format(len(resp.content)))
                    problema2 = True
                else:
                    print("[ERRO] Nao e PDF valido")
                    problema2 = False
            else:
                print("[ERRO] Status {}".format(resp.status_code))
                problema2 = False
        except Exception as e:
            print("[ERRO] {}".format(str(e)[:80]))
            problema2 = False
    else:
        print("[SKIP]")
        problema2 = None

    print("\nPROBLEMA 3: GELO NAO EM RETORNO")
    resp = requests.get(f"{BASE_URL}/api/produtos", headers=headers)
    gelo_api = next((p for p in resp.json()['items'] if p['id'] == gelo['id']), None)
    if gelo_api['nao_devolve']:
        print("[OK] Gelo marcado como nao_devolve=True")
        problema3 = True
    else:
        print("[ERRO] nao_devolve=False")
        problema3 = False

    print("\nRESUMO:")
    print("1: {}".format("OK" if problema1 else "ERRO"))
    print("2: {}".format("OK" if problema2 else ("ERRO" if problema2 is not None else "SKIP")))
    print("3: {}".format("OK" if problema3 else "ERRO"))
    
except Exception as e:
    print("[ERRO] {}".format(e))
    import traceback
    traceback.print_exc()
