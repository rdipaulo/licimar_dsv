#!/usr/bin/env python3
"""
Teste completo: Login -> Criar Pedido -> Gerar PDF
"""
import requests
import json

base_url = "http://127.0.0.1:5000"

print("[TEST] 1. Fazendo login...")
login_resp = requests.post(f"{base_url}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Login OK")

print("\n[TEST] 2. Buscando clientes ativos...")
clientes_resp = requests.get(f"{base_url}/api/ambulantes/ativos", headers=headers)
clientes = clientes_resp.json()
if clientes:
    cliente_id = clientes[0]["id"]
    print(f"✅ Cliente encontrado: ID {cliente_id}")
else:
    print("❌ Nenhum cliente ativo encontrado")
    exit(1)

print("\n[TEST] 3. Buscando produtos...")
produtos_resp = requests.get(f"{base_url}/api/produtos?per_page=100", headers=headers)
produtos = produtos_resp.json()["items"]
if produtos:
    # Procurar gelo seco
    gelo = [p for p in produtos if 'gelo' in p['nome'].lower()]
    if gelo:
        produto_id = gelo[0]["id"]
        print(f"✅ Gelo seco encontrado: ID {produto_id} - {gelo[0]['nome']}")
    else:
        produto_id = produtos[0]["id"]
        print(f"✅ Primeiro produto: ID {produto_id} - {produtos[0]['nome']}")
else:
    print("❌ Nenhum produto encontrado")
    exit(1)

print("\n[TEST] 4. Criando novo pedido de saída...")
payload = {
    "cliente_id": cliente_id,
    "itens_saida": [
        {"produto_id": produto_id, "quantidade_saida": 2.5}
    ]
}
pedido_resp = requests.post(f"{base_url}/api/pedidos/saida", json=payload, headers=headers)
print(f"Status: {pedido_resp.status_code}")

if pedido_resp.status_code in [200, 201]:
    pedido_data = pedido_resp.json()
    pedido_id = pedido_data.get("id") or pedido_data.get("pedido", {}).get("id")
    print(f"✅ Pedido criado: ID {pedido_id}")
    print(f"Resposta: {json.dumps(pedido_data, indent=2, default=str)}")
else:
    print(f"❌ Erro ao criar pedido: {pedido_resp.text}")
    exit(1)

print(f"\n[TEST] 5. Gerando PDF do pedido {pedido_id}...")
pdf_resp = requests.get(f"{base_url}/api/pedidos/{pedido_id}/imprimir", headers=headers)
print(f"Status: {pdf_resp.status_code}")
print(f"Content-Type: {pdf_resp.headers.get('Content-Type')}")
print(f"Size: {len(pdf_resp.content)} bytes")

if pdf_resp.status_code == 200:
    with open(f'pedido_{pedido_id}.pdf', 'wb') as f:
        f.write(pdf_resp.content)
    print(f"✅ PDF salvo: pedido_{pedido_id}.pdf")
else:
    print(f"❌ Erro ao gerar PDF: {pdf_resp.text}")
