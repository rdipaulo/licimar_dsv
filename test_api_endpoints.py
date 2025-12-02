#!/usr/bin/env python3
"""
Teste rápido dos endpoints da API
"""
import requests
import json
import sys
import os

# Adiciona o caminho para importar o app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/licimar_mvp_app'))

from src.main import create_app
from src.database import db
from src.models import Cliente, User, Produto

def get_test_token():
    """Obtém um token de teste"""
    app = create_app('development')
    with app.app_context():
        # Verifica se existe usuário
        user = User.query.first()
        if not user:
            print("Criando usuário de teste...")
            user = User(email='test@test.com', nome='Test User')
            user.set_password('123456')
            db.session.add(user)
            db.session.commit()
        
        # Retorna dados do usuário
        return {
            'email': user.email,
            'password': '123456',
            'id': user.id
        }

def test_endpoints():
    """Testa os endpoints da API"""
    print("="*70)
    print("TESTE DE ENDPOINTS DA API")
    print("="*70)
    
    app = create_app('development')
    
        # Teste 1: Login
        print("\n[1] Testando Login...")
        with app.test_client() as client:
            # Primeiro, cria usuário se não existir
            with app.app_context():
                user = User.query.first()
                if not user:
                    user = User(email='test@test.com', nome='Test User')
                    user.set_password('123456')
                    db.session.add(user)
                    db.session.commit()        # Faz login
        response = client.post('/api/auth/login', 
            json={'email': 'test@test.com', 'password': '123456'},
            headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            token = response.json.get('token')
            print(f"    ✓ Login bem-sucedido")
            print(f"    ✓ Token: {token[:20]}...")
        else:
            print(f"    ✗ Erro no login: {response.status_code}")
            print(f"    Resposta: {response.json}")
            return
        
        # Teste 2: Clientes Ativos
        print("\n[2] Testando GET /api/clientes/ativos...")
        response = client.get('/api/clientes/ativos',
            headers={'Authorization': f'Bearer {token}'})
        
        if response.status_code == 200:
            clientes = response.json
            print(f"    ✓ Clientes carregados: {len(clientes)}")
            if clientes:
                print(f"    Primeiro cliente: {clientes[0]}")
        else:
            print(f"    ✗ Erro: {response.status_code}")
            print(f"    Resposta: {response.json}")
        
        # Teste 3: Produtos
        print("\n[3] Testando GET /api/produtos...")
        response = client.get('/api/produtos',
            headers={'Authorization': f'Bearer {token}'})
        
        if response.status_code == 200:
            produtos_data = response.json
            print(f"    ✓ Produtos carregados")
            if isinstance(produtos_data, dict):
                count = produtos_data.get('total', 0)
                print(f"    Total de produtos: {count}")
            else:
                print(f"    Tipo de resposta: {type(produtos_data)}")
        else:
            print(f"    ✗ Erro: {response.status_code}")
            print(f"    Resposta: {response.json}")
        
        # Teste 4: Clientes (paginated)
        print("\n[4] Testando GET /api/clientes...")
        response = client.get('/api/clientes',
            headers={'Authorization': f'Bearer {token}'})
        
        if response.status_code == 200:
            clientes_data = response.json
            print(f"    ✓ Clientes carregados")
            print(f"    Resposta: {clientes_data}")
        else:
            print(f"    ✗ Erro: {response.status_code}")
            print(f"    Resposta: {response.json}")
        
        # Teste 5: Ambulantes
        print("\n[5] Testando GET /api/ambulantes...")
        response = client.get('/api/ambulantes',
            headers={'Authorization': f'Bearer {token}'})
        
        if response.status_code == 200:
            ambulantes = response.json
            print(f"    ✓ Ambulantes carregados: {len(ambulantes)}")
        else:
            print(f"    ✗ Erro: {response.status_code}")
            print(f"    Resposta: {response.json}")
        
        # Teste 6: Pedidos
        print("\n[6] Testando GET /api/pedidos...")
        response = client.get('/api/pedidos?status=saida',
            headers={'Authorization': f'Bearer {token}'})
        
        if response.status_code == 200:
            pedidos_data = response.json
            print(f"    ✓ Pedidos carregados")
            if isinstance(pedidos_data, dict):
                print(f"    Resposta type: dict")
                print(f"    Keys: {list(pedidos_data.keys())}")
            else:
                print(f"    Resposta type: {type(pedidos_data)}")
        else:
            print(f"    ✗ Erro: {response.status_code}")
            print(f"    Resposta: {response.json}")
    
    print("\n" + "="*70)
    print("TESTE CONCLUÍDO")
    print("="*70)

if __name__ == '__main__':
    test_endpoints()
