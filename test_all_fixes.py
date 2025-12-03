#!/usr/bin/env python
"""
Script de testes para verificar se todos os 5 problemas estão resolvidos
"""
import requests
import json
from datetime import datetime
import time

BASE_URL = "http://127.0.0.1:5000"
TOKEN = None

def log_test(name, result, details=""):
    status = "✅ PASSOU" if result else "❌ FALHOU"
    print(f"\n[TEST] {name}: {status}")
    if details:
        print(f"       {details}")

def login():
    """Faz login e retorna o token"""
    global TOKEN
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        TOKEN = response.json()['access_token']
        log_test("Login", True, f"Token obtido: {TOKEN[:20]}...")
        return True
    else:
        log_test("Login", False, f"Status: {response.status_code}")
        return False

def get_headers():
    """Retorna headers com token de autenticação"""
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

# ===== TESTE 1: Produtos Duplicados =====
def test_produtos_duplicados():
    """Testa se produtos duplicados foram removidos e validação está ativa"""
    print("\n" + "="*60)
    print("TESTE 1: PRODUTOS DUPLICADOS")
    print("="*60)
    
    url = f"{BASE_URL}/api/produtos?per_page=100"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code != 200:
        log_test("Listar Produtos", False, f"Status: {response.status_code}")
        return
    
    produtos = response.json()['items']
    
    # Verifica duplicados por nome+categoria
    nome_categoria_map = {}
    duplicados = []
    
    for p in produtos:
        key = f"{p['nome'].lower()}_{p['categoria_id']}"
        if key in nome_categoria_map:
            duplicados.append(p['nome'])
        else:
            nome_categoria_map[key] = p['id']
    
    log_test("Sem Duplicados", len(duplicados) == 0, 
             f"Total de produtos: {len(produtos)} | Duplicados encontrados: {duplicados if duplicados else 'nenhum'}")
    
    # Tenta criar um produto que já existe (deve falhar)
    produto_existente = produtos[0] if produtos else None
    if produto_existente:
        url = f"{BASE_URL}/api/produtos"
        data = {
            "nome": produto_existente['nome'],
            "categoria_id": produto_existente['categoria_id'],
            "preco": 10.0,
            "active": True
        }
        response = requests.post(url, json=data, headers=get_headers())
        
        # Deve retornar 409 (Conflict)
        resultado = response.status_code == 409
        log_test("Validação Duplicados", resultado, 
                 f"Tentou criar '{produto_existente['nome']}' | Status: {response.status_code}")

# ===== TESTE 2: Gelo Seco =====
def test_gelo_seco():
    """Testa se é possível inserir gelo seco com valores decimais"""
    print("\n" + "="*60)
    print("TESTE 2: GELO SECO (CAMPOS DECIMAIS)")
    print("="*60)
    
    # Obter clientes ativos
    url = f"{BASE_URL}/api/clientes/ativos"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code != 200 or not response.json():
        log_test("Listar Clientes", False, f"Status: {response.status_code}")
        return
    
    cliente_id = response.json()[0]['id']
    
    # Obter gelo seco
    url = f"{BASE_URL}/api/produtos?search=gelo&per_page=100"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code != 200:
        log_test("Encontrar Gelo", False, f"Status: {response.status_code}")
        return
    
    produtos = response.json()['items']
    gelo = next((p for p in produtos if 'gelo' in p['nome'].lower()), None)
    
    if not gelo:
        log_test("Encontrar Gelo", False, "Produto 'gelo' não encontrado no banco")
        return
    
    log_test("Encontrar Gelo", True, f"Gelo encontrado: {gelo['nome']} (ID: {gelo['id']})")
    
    # Criar pedido com gelo seco (quantidade decimal)
    url = f"{BASE_URL}/api/pedidos/saida"
    data = {
        "cliente_id": cliente_id,
        "itens_saida": [
            {
                "produto_id": gelo['id'],
                "quantidade_saida": 2.5  # Quantidade decimal
            }
        ]
    }
    
    response = requests.post(url, json=data, headers=get_headers())
    resultado = response.status_code == 201
    
    log_test("Criar Pedido com Gelo Decimal", resultado, 
             f"Quantidade: 2.5 kg | Status: {response.status_code}")
    
    if resultado:
        pedido_id = response.json()['pedido']['id']
        
        # Tenta registrar retorno com gelo decimal
        url = f"{BASE_URL}/api/pedidos/{pedido_id}/retorno"
        data = {
            "itens": [
                {
                    "produto_id": gelo['id'],
                    "quantidade_retorno": 1.25  # Quantidade decimal
                }
            ],
            "gelo_kg": 2.5,  # Campo de gelo retorno
            "divida": 0.0
        }
        
        response = requests.post(url, json=data, headers=get_headers())
        resultado = response.status_code == 200
        
        log_test("Registrar Retorno com Gelo Decimal", resultado, 
                 f"Retorno: 1.25 kg | Gelo Retorno: 2.5 kg | Status: {response.status_code}")

# ===== TESTE 3: Data/Hora em Brasília =====
def test_data_hora_brasilia():
    """Testa se datas/horas estão em Brasília (GMT-3)"""
    print("\n" + "="*60)
    print("TESTE 3: DATA/HORA BRASÍLIA (GMT-3)")
    print("="*60)
    
    # Criar um novo cliente
    url = f"{BASE_URL}/api/clientes"
    data = {
        "nome": f"Cliente Teste {int(time.time())}",
        "email": f"test{int(time.time())}@test.com",
        "telefone": "21999999999"
    }
    
    response = requests.post(url, json=data, headers=get_headers())
    
    if response.status_code != 201:
        log_test("Criar Cliente para Teste", False, f"Status: {response.status_code}")
        return
    
    cliente_resposta = response.json()['cliente']
    created_at = cliente_resposta.get('created_at')
    
    if not created_at:
        log_test("Data de Criação", False, "Campo 'created_at' não retornou")
        return
    
    # Parse da data
    try:
        data_obj = datetime.fromisoformat(created_at)
        agora = datetime.now()
        
        # A data deve estar próxima da hora atual (dentro de 5 segundos)
        diff = abs((agora - data_obj).total_seconds())
        resultado = diff < 5
        
        log_test("Timestamp em Brasília", resultado, 
                 f"Data: {created_at} | Diferença: {diff:.1f}s (esperado < 5s)")
    except Exception as e:
        log_test("Timestamp em Brasília", False, f"Erro ao parsear: {e}")

# ===== TESTE 4: Campo Dívida sem Limitação =====
def test_campo_divida():
    """Testa se o campo de dívida aceita valores grandes"""
    print("\n" + "="*60)
    print("TESTE 4: CAMPO DÍVIDA (SEM LIMITAÇÃO)")
    print("="*60)
    
    # Obter cliente e criar pedido
    url = f"{BASE_URL}/api/clientes/ativos"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code != 200 or not response.json():
        log_test("Listar Clientes", False, f"Status: {response.status_code}")
        return
    
    cliente_id = response.json()[0]['id']
    
    # Obter um produto qualquer
    url = f"{BASE_URL}/api/produtos?per_page=1"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code != 200 or not response.json()['items']:
        log_test("Listar Produtos", False, f"Status: {response.status_code}")
        return
    
    produto_id = response.json()['items'][0]['id']
    
    # Criar pedido
    url = f"{BASE_URL}/api/pedidos/saida"
    data = {
        "cliente_id": cliente_id,
        "itens_saida": [
            {
                "produto_id": produto_id,
                "quantidade_saida": 1
            }
        ]
    }
    
    response = requests.post(url, json=data, headers=get_headers())
    
    if response.status_code != 201:
        log_test("Criar Pedido", False, f"Status: {response.status_code}")
        return
    
    pedido_id = response.json()['pedido']['id']
    
    # Registrar retorno com dívida GRANDE (sem limitação)
    url = f"{BASE_URL}/api/pedidos/{pedido_id}/retorno"
    
    # Testa valores grandes em dívida
    valores_teste = [999.99, 1234.56, 9999.99]
    
    for valor_divida in valores_teste:
        data = {
            "itens": [
                {
                    "produto_id": produto_id,
                    "quantidade_retorno": 1
                }
            ],
            "divida": valor_divida
        }
        
        response = requests.post(url, json=data, headers=get_headers())
        
        # Se falhar na primeira tentativa, quebra o loop
        if response.status_code != 200:
            log_test(f"Registrar Dívida R$ {valor_divida}", False, 
                     f"Status: {response.status_code} | Resposta: {response.text[:100]}")
            break
        else:
            log_test(f"Registrar Dívida R$ {valor_divida}", True, 
                     f"Dívida aceita com sucesso")
            
            # Cria um novo pedido para o próximo teste
            url = f"{BASE_URL}/api/pedidos/saida"
            data = {
                "cliente_id": cliente_id,
                "itens_saida": [
                    {
                        "produto_id": produto_id,
                        "quantidade_saida": 1
                    }
                ]
            }
            response = requests.post(url, json=data, headers=get_headers())
            if response.status_code == 201:
                pedido_id = response.json()['pedido']['id']
                url = f"{BASE_URL}/api/pedidos/{pedido_id}/retorno"
            else:
                break

# ===== TESTE 5: Print e Fechamento de Pedido =====
def test_print_fechamento():
    """Testa se pedido é fechado e print funciona após retorno"""
    print("\n" + "="*60)
    print("TESTE 5: PRINT E FECHAMENTO DE PEDIDO")
    print("="*60)
    
    # Obter cliente
    url = f"{BASE_URL}/api/clientes/ativos"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code != 200 or not response.json():
        log_test("Listar Clientes", False, f"Status: {response.status_code}")
        return
    
    cliente_id = response.json()[0]['id']
    
    # Obter um produto
    url = f"{BASE_URL}/api/produtos?per_page=1"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code != 200 or not response.json()['items']:
        log_test("Listar Produtos", False, f"Status: {response.status_code}")
        return
    
    produto_id = response.json()['items'][0]['id']
    
    # Criar pedido
    url = f"{BASE_URL}/api/pedidos/saida"
    data = {
        "cliente_id": cliente_id,
        "itens_saida": [
            {
                "produto_id": produto_id,
                "quantidade_saida": 5
            }
        ]
    }
    
    response = requests.post(url, json=data, headers=get_headers())
    
    if response.status_code != 201:
        log_test("Criar Pedido", False, f"Status: {response.status_code}")
        return
    
    pedido_id = response.json()['pedido']['id']
    
    # Registrar retorno (deve fechar pedido)
    url = f"{BASE_URL}/api/pedidos/{pedido_id}/retorno"
    data = {
        "itens": [
            {
                "produto_id": produto_id,
                "quantidade_retorno": 3
            }
        ],
        "divida": 0.0
    }
    
    response = requests.post(url, json=data, headers=get_headers())
    
    if response.status_code != 200:
        log_test("Registrar Retorno", False, f"Status: {response.status_code}")
        return
    
    # Verifica se pedido foi fechado
    url = f"{BASE_URL}/api/pedidos/{pedido_id}"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code != 200:
        log_test("Verificar Status Pedido", False, f"Status: {response.status_code}")
        return
    
    pedido = response.json()
    status = pedido.get('status')
    
    resultado = status == 'finalizado'
    log_test("Pedido Finalizado", resultado, f"Status: {status} (esperado: finalizado)")
    
    # Testa impressão da nota de retorno
    url = f"{BASE_URL}/api/pedidos/{pedido_id}/imprimir_retorno"
    response = requests.get(url, headers=get_headers())
    
    resultado = response.status_code == 200 and response.headers.get('Content-Type') == 'application/pdf'
    log_test("Gerar PDF de Retorno", resultado, 
             f"Status: {response.status_code} | Content-Type: {response.headers.get('Content-Type', 'não definido')}")

def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("TESTES LICIMAR MVP - VALIDAÇÃO DE CORREÇÕES")
    print("="*60)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    
    # Login
    if not login():
        print("\n❌ Não foi possível fazer login. Abortando testes.")
        return
    
    # Executar testes
    test_produtos_duplicados()
    test_gelo_seco()
    test_data_hora_brasilia()
    test_campo_divida()
    test_print_fechamento()
    
    print("\n" + "="*60)
    print("TESTES CONCLUÍDOS")
    print("="*60)

if __name__ == "__main__":
    main()
