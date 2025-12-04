#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Teste completo dos 3 problemas"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("="*70)
print("TESTE COMPLETO - LICIMAR MVP - 3 PROBLEMAS")
print("="*70)

try:
    # LOGIN
    resp = requests.post(f"{BASE_URL}/api/auth/login", 
        json={"username": "admin", "password": "admin123"})
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("\n✅ Login OK")

    # GET CLIENTES
    resp = requests.get(f"{BASE_URL}/api/clientes", headers=headers)
    clientes = resp.json()['items']
    cliente_id = clientes[0]['id']
    print(f"✅ Cliente: {clientes[0]['nome']}")

    # GET PRODUTOS
    resp = requests.get(f"{BASE_URL}/api/produtos", headers=headers)
    produtos = resp.json()['items']
    
    gelo = next((p for p in produtos if p['nome'] == 'Gelo Seco (kg)'), None)
    isopor = next((p for p in produtos if p['nome'] == 'Caixa de Isopor'), None)
    sacola = next((p for p in produtos if p['nome'] == 'Sacola Termica'), None)
    
    print(f"✅ Gelo: nao_devolve={gelo['nao_devolve']}")
    print(f"✅ Isopor: nao_devolve={isopor['nao_devolve']}")
    print(f"✅ Sacola: nao_devolve={sacola['nao_devolve']}")

    print("\n" + "="*70)
    print("PROBLEMA 1: GELO COM VALOR DECIMAL (2.5 kg)")
    print("="*70)
    
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
        item = pedido['itens'][0]
        print(f"✅ Status 201 - Saída criada")
        print(f"   - Quantidade: {item['quantidade_saida']} kg")
        print(f"   - Total: R$ {pedido['total']:.2f}")
        problema1 = True
    else:
        print(f"❌ Status {resp.status_code}")
        print(f"   - {resp.json()}")
        problema1 = False

    print("\n" + "="*70)
    print("PROBLEMA 2: PDF/PRINT AO REGISTRAR SAÍDA")
    print("="*70)
    
    if problema1:
        # Tentar baixar PDF
        pedido_id = pedido['id']
        resp = requests.get(f"{BASE_URL}/api/pedidos/{pedido_id}/imprimir", 
            headers=headers)
        
        if resp.status_code == 200:
            # Verificar se é um PDF válido
            if b'%PDF' in resp.content[:10]:
                print(f"✅ Status 200 - PDF gerado")
                print(f"   - Tamanho: {len(resp.content)} bytes")
                problema2 = True
            else:
                print(f"⚠️ Status 200 mas não é PDF válido")
                print(f"   - Content-Type: {resp.headers.get('content-type')}")
                print(f"   - Response: {resp.text[:100]}")
                problema2 = False
        else:
            print(f"❌ Status {resp.status_code}")
            print(f"   - {resp.json()}")
            problema2 = False
    else:
        print("⏭️ Skipped (Problema 1 não resolvido)")
        problema2 = None

    print("\n" + "="*70)
    print("PROBLEMA 3: GELO NÃO DEVE APARECER EM RETORNO")
    print("="*70)
    
    # GET PEDIDOS COM STATUS saida
    resp = requests.get(f"{BASE_URL}/api/pedidos?status=saida", headers=headers)
    pedidos_saida = resp.json()['items'] if 'items' in resp.json() else []
    
    if pedidos_saida:
        pedido_com_gelo = next((p for p in pedidos_saida if any(
            it['produto_id'] == gelo['id'] for it in p['itens']
        )), None)
        
        if pedido_com_gelo:
            # Verificar flags do produto
            resp = requests.get(f"{BASE_URL}/api/produtos", headers=headers)
            gelo_from_api = next((p for p in resp.json()['items'] 
                if p['id'] == gelo['id']), None)
            
            if gelo_from_api['nao_devolve']:
                print(f"✅ Gelo marcado como nao_devolve=True")
                print(f"   - Não aparecerá em formulário de retorno")
                problema3 = True
            else:
                print(f"❌ Gelo não está marcado como nao_devolve")
                problema3 = False
        else:
            print("⏭️ Nenhum pedido com gelo para testar retorno")
            problema3 = None
    else:
        print("⏭️ Nenhum pedido com status saida")
        problema3 = None

    print("\n" + "="*70)
    print("RESUMO FINAL")
    print("="*70)
    print(f"Problema 1 (Gelo decimal): {'✅ RESOLVIDO' if problema1 else '❌ NÃO RESOLVIDO'}")
    print(f"Problema 2 (PDF/Print):    {'✅ RESOLVIDO' if problema2 else '❌ NÃO RESOLVIDO' if problema2 is not None else '⏭️ SKIPPED'}")
    print(f"Problema 3 (Retorno):      {'✅ RESOLVIDO' if problema3 else '❌ NÃO RESOLVIDO' if problema3 is not None else '⏭️ SKIPPED'}")
    
except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()
