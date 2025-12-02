#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test criar pedido de saida"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/licimar_mvp_app'))

from src.main import create_app
from src.database import db
from src.models import Produto, Cliente

app = create_app('development')

with app.test_client() as client:
    with app.app_context():
        # 1. Login
        print("[1] Fazendo login...")
        response = client.post('/api/auth/login', 
            json={'username': 'admin', 'password': 'admin123'},
            headers={'Content-Type': 'application/json'})
        
        if response.status_code != 200:
            print("ERROR: Login falhou: {}".format(response.json))
            sys.exit(1)
        
        token = response.json.get('access_token') or response.json.get('token')
        print("[OK] Login bem-sucedido")
        
        # 2. Pega primeiro cliente e produto
        print("\n[2] Obtendo dados...")
        cliente = Cliente.query.first()
        produto = Produto.query.first()
        
        if not cliente:
            print("ERROR: Nenhum cliente disponivel")
            sys.exit(1)
        
        if not produto:
            print("ERROR: Nenhum produto disponivel")
            sys.exit(1)
        
        print("[OK] Cliente: {} (ID: {})".format(cliente.nome, cliente.id))
        print("[OK] Produto: {} (ID: {})".format(produto.nome, produto.id))
        
        # 3. Cria pedido de saida
        print("\n[3] Criando pedido de saida...")
        payload = {
            'cliente_id': cliente.id,
            'itens_saida': [
                {
                    'produto_id': produto.id,
                    'quantidade_saida': 5
                }
            ]
        }
        
        response = client.post('/api/pedidos/saida',
            json=payload,
            headers={
                'Authorization': 'Bearer {}'.format(token),
                'Content-Type': 'application/json'
            })
        
        print("Status: {}".format(response.status_code))
        
        if response.status_code in [200, 201]:
            data = response.json
            print("[OK] Pedido criado com sucesso!")
            pedido_id = data.get('pedido', {}).get('id')
            print("  - ID: {}".format(pedido_id))
            print("  - Status: {}".format(data.get('pedido', {}).get('status')))
            print("  - Total: {}".format(data.get('pedido', {}).get('total')))
        else:
            print("[ERROR] Falha ao criar pedido: {}".format(response.json))
            sys.exit(1)
        
        # 4. Verifica se pedido aparece em GET /pedidos
        print("\n[4] Verificando pedido na lista...")
        response = client.get('/api/pedidos?status=saida',
            headers={'Authorization': 'Bearer {}'.format(token)})
        
        if response.status_code == 200:
            items = response.json.get('items', [])
            print("[OK] Total de pedidos em aberto: {}".format(len(items)))
            if items:
                for item in items:
                    print("  - Pedido #{}: {} ({})".format(
                        item.get('id'),
                        item.get('cliente_nome'),
                        item.get('status')
                    ))
        else:
            print("[ERROR] Falha ao listar pedidos: {}".format(response.json))
        
        print("\n[SUCCESS] Teste concluido!")
