#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test API response data"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/licimar_mvp_app'))

from src.main import create_app
from src.database import db
from src.models import Produto, Categoria

app = create_app('development')

with app.app_context():
    # Criar produtos se não existir
    print("Verificando produtos no banco...")
    
    cat = Categoria.query.first()
    if not cat:
        print("Criando categorias...")
        for nome in ['Kibon', 'Nestle', 'Italia']:
            cat = Categoria(nome=nome, active=True)
            db.session.add(cat)
        db.session.commit()
    
    cat_id = Categoria.query.first().id
    
    produtos_existentes = Produto.query.count()
    if produtos_existentes < 5:
        print("Criando produtos...")
        produtos_dados = [
            {'nome': 'Picolé Chicabon', 'preco': 2.50, 'estoque': 100},
            {'nome': 'Cone Crocante', 'preco': 3.50, 'estoque': 80},
            {'nome': 'Brigadeiro', 'preco': 1.50, 'estoque': 200},
        ]
        for dados in produtos_dados:
            prod = Produto(
                nome=dados['nome'],
                preco=dados['preco'],
                estoque=dados['estoque'],
                categoria_id=cat_id,
                active=True
            )
            db.session.add(prod)
        db.session.commit()
        print("Produtos criados")
    
    # Test API
    print("\nTestando API...")
    with app.test_client() as client:
        # Criar usuário
        from src.models import User
        user = User.query.filter_by(username='testuser').first()
        if not user:
            user = User(username='testuser', email='test@test.com')
            user.set_password('123456')
            db.session.add(user)
            db.session.commit()
        
        # Login
        response = client.post('/api/auth/login', 
            json={'username': 'testuser', 'password': '123456'})
        
        if response.status_code != 200:
            print("Login failed: {} - {}".format(response.status_code, response.json))
            sys.exit(1)
        
        token = response.json.get('token') or response.json.get('access_token')
        if not token:
            print("ERROR: No token in response: {}".format(response.json))
            sys.exit(1)
        
        print("Login OK - Token: {}...".format(token[:20]))
        
        # Testa GET /api/produtos
        print("\n[1] GET /api/produtos")
        response = client.get('/api/produtos',
            headers={'Authorization': 'Bearer {}'.format(token)})
        
        if response.status_code == 200:
            data = response.json
            print("Status: {}".format(response.status_code))
            print("Response type: {}".format(type(data).__name__))
            if isinstance(data, dict):
                print("Keys: {}".format(list(data.keys())))
                if 'items' in data:
                    print("Number of items: {}".format(len(data['items'])))
                    if data['items']:
                        print("First item: {}".format(data['items'][0]))
        else:
            print("ERROR: {} - {}".format(response.status_code, response.json))
        
        # Testa GET /api/clientes
        print("\n[2] GET /api/clientes")
        response = client.get('/api/clientes',
            headers={'Authorization': 'Bearer {}'.format(token)})
        
        if response.status_code == 200:
            data = response.json
            print("Status: {}".format(response.status_code))
            if isinstance(data, dict):
                print("Keys: {}".format(list(data.keys())))
                if 'items' in data:
                    print("Number of items: {}".format(len(data['items'])))
        else:
            print("ERROR: {} - {}".format(response.status_code, response.json))
        
        # Testa GET /api/clientes/ativos
        print("\n[3] GET /api/clientes/ativos")
        response = client.get('/api/clientes/ativos',
            headers={'Authorization': 'Bearer {}'.format(token)})
        
        if response.status_code == 200:
            data = response.json
            print("Status: {}".format(response.status_code))
            print("Response type: {}".format(type(data).__name__))
            print("Number of items: {}".format(len(data)))
            if data:
                print("First item: {}".format(data[0]))
        else:
            print("ERROR: {} - {}".format(response.status_code, response.json))
