#!/usr/bin/env python3
"""Teste rápido dos endpoints da API"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/licimar_mvp_app'))

from src.main import create_app
from src.database import db
from src.models import User, Cliente, Produto

app = create_app('development')

with app.app_context():
    # Criar usuário de teste
    user = User.query.filter_by(username='testuser').first()
    if not user:
        user = User(username='testuser', email='test@test.com')
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()
        print(f"[SETUP] Usuário criado: testuser")
    else:
        print(f"[SETUP] Usuário já existe: testuser")

with app.test_client() as client:
    
    print("="*70)
    print("TESTE DE ENDPOINTS DA API")
    print("="*70)
    
    # Login
    print("\n[1] Testando Login...")
    response = client.post('/api/auth/login', 
        json={'username': 'testuser', 'password': '123456'},
        headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        data = response.json
        print(f"    ✓ Login bem-sucedido")
        print(f"    Resposta: {data}")
        token = data.get('token') or data.get('access_token')
        print(f"    Token obtido: {token[:20] if token else 'NONE'}...")
    else:
        print(f"    ✗ Erro: {response.status_code} - {response.json}")
        sys.exit(1)
    
    # Teste 2: Clientes Ativos
    print("\n[2] GET /api/clientes/ativos...")
    response = client.get('/api/clientes/ativos',
        headers={'Authorization': f'Bearer {token}'})
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        print(f"    ✓ Retornou: {type(response.json)} com {len(response.json)} itens")
    else:
        print(f"    ✗ Erro: {response.json}")
    
    # Teste 3: Produtos
    print("\n[3] GET /api/produtos...")
    response = client.get('/api/produtos',
        headers={'Authorization': f'Bearer {token}'})
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json
        if isinstance(data, dict):
            print(f"    ✓ Retornou dict com keys: {list(data.keys())}")
        else:
            print(f"    ✓ Retornou: {type(data)}")
    else:
        print(f"    ✗ Erro: {response.json}")
    
    # Teste 4: Clientes (paginated)
    print("\n[4] GET /api/clientes...")
    response = client.get('/api/clientes',
        headers={'Authorization': f'Bearer {token}'})
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json
        if isinstance(data, dict):
            print(f"    ✓ Retornou dict com keys: {list(data.keys())}")
        else:
            print(f"    ✓ Retornou: {type(data)}")
    else:
        print(f"    ✗ Erro: {response.json}")
    
    print("\n" + "="*70)
    print("TESTE CONCLUÍDO")
    print("="*70)
