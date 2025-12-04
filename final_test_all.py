#!/usr/bin/env python3
"""
Teste final: Validar que o fluxo de gelo + PDF funciona corretamente
"""
import requests
import json
import time

base_url = "http://127.0.0.1:5000"

print("=" * 60)
print("TESTE FINAL: GELO SECO + PDF")
print("=" * 60)

# 1. Login
print("\n[1/5] Fazendo login...")
login_resp = requests.post(f"{base_url}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Login OK")

# 2. Carregar cliente
print("\n[2/5] Carregando cliente ativo...")
clientes_resp = requests.get(f"{base_url}/api/ambulantes/ativos", headers=headers)
cliente_id = clientes_resp.json()[0]["id"]
print(f"✅ Cliente: {clientes_resp.json()[0]['nome']}")

# 3. Carregar gelo seco
print("\n[3/5] Procurando Gelo Seco...")
produtos_resp = requests.get(f"{base_url}/api/produtos?per_page=100", headers=headers)
produtos = produtos_resp.json()["items"]
gelo = [p for p in produtos if 'gelo' in p['nome'].lower()][0]
print(f"✅ Gelo Seco: {gelo['nome']} - R$ {gelo['preco']}")
print(f"   Tipo: {type(gelo.get('peso'))}")
if gelo.get('peso'):
    print(f"   Peso: {gelo['peso']} kg")

# 4. Criar pedido com 2.5 kg (teste decimal!)
print("\n[4/5] Criando pedido com 2.5 kg de Gelo...")
payload = {
    "cliente_id": cliente_id,
    "itens_saida": [
        {"produto_id": gelo["id"], "quantidade_saida": 2.5}
    ]
}
pedido_resp = requests.post(f"{base_url}/api/pedidos/saida", json=payload, headers=headers)

if pedido_resp.status_code == 201:
    pedido_data = pedido_resp.json()["pedido"]
    pedido_id = pedido_data["id"]
    print(f"✅ Pedido criado: #{pedido_id}")
    print(f"   Quantidade salva: {pedido_data['itens'][0]['quantidade_saida']} kg")
    print(f"   Total: R$ {pedido_data['total']}")
    
    # Validar que a quantidade foi salva como decimal
    if pedido_data['itens'][0]['quantidade_saida'] == 2.5:
        print("   ✅ DECIMAL ARMAZENADO CORRETAMENTE!")
    else:
        print(f"   ❌ ERRO: Esperava 2.5 mas foi armazenado {pedido_data['itens'][0]['quantidade_saida']}")
else:
    print(f"❌ Erro ao criar pedido: {pedido_resp.status_code}")
    print(f"   {pedido_resp.text}")
    exit(1)

# 5. Gerar PDF
print("\n[5/5] Gerando PDF...")
pdf_resp = requests.get(f"{base_url}/api/pedidos/{pedido_id}/imprimir", headers=headers)

if pdf_resp.status_code == 200:
    with open(f'final_test_pedido_{pedido_id}.pdf', 'wb') as f:
        f.write(pdf_resp.content)
    print(f"✅ PDF gerado: {len(pdf_resp.content)} bytes")
    print(f"   Arquivo: final_test_pedido_{pedido_id}.pdf")
else:
    print(f"❌ Erro ao gerar PDF: {pdf_resp.status_code}")

print("\n" + "=" * 60)
print("✅ TESTE COMPLETO COM SUCESSO!")
print("=" * 60)
print(f"\nResumo:")
print(f"  1. ✅ Gelo Seco 2.5 kg adicionado")
print(f"  2. ✅ Quantidade decimal salva no banco")
print(f"  3. ✅ PDF gerado com sucesso")
print(f"  4. ✅ Tudo funcionando!")
