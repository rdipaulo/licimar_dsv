#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup banco de dados com dados de teste"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/licimar_mvp_app'))

from src.main import create_app
from src.database import db
from src.models import User, Categoria, Cliente, Produto

def setup_database():
    """Setup banco de dados"""
    app = create_app('development')
    
    with app.app_context():
        print("[SETUP] Criando tabelas...")
        db.create_all()
        
        # 1. Criar usuário admin
        print("[SETUP] Criando usuario admin...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@licimar.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("  [OK] Admin criado (login: admin / senha: admin123)")
        else:
            print("  [OK] Admin ja existe")
        
        # 2. Criar categorias
        print("[SETUP] Criando categorias...")
        categorias_dados = [
            {'nome': 'Kibon', 'descricao': 'Produtos Kibon'},
            {'nome': 'Nestle', 'descricao': 'Produtos Nestle'},
            {'nome': 'Italia', 'descricao': 'Produtos Italia'},
            {'nome': 'Gelo', 'descricao': 'Gelo seco'},
            {'nome': 'Acessorios', 'descricao': 'Acessorios'},
            {'nome': 'Outros', 'descricao': 'Outros produtos'},
        ]
        categorias_dict = {}
        for cat_data in categorias_dados:
            cat = Categoria.query.filter_by(nome=cat_data['nome']).first()
            if not cat:
                cat = Categoria(nome=cat_data['nome'], descricao=cat_data['descricao'], active=True)
                db.session.add(cat)
                print("  [OK] Categoria {} criada".format(cat_data['nome']))
            categorias_dict[cat_data['nome']] = cat
        
        db.session.commit()
        
        # 3. Criar produtos
        print("[SETUP] Criando produtos...")
        produtos_dados = [
            {'nome': 'Picolé Chicabon', 'preco': 2.50, 'estoque': 100, 'categoria': 'Kibon'},
            {'nome': 'Picolé Chicabon Zero', 'preco': 3.00, 'estoque': 80, 'categoria': 'Kibon'},
            {'nome': 'Eskibon Classico', 'preco': 2.75, 'estoque': 120, 'categoria': 'Kibon'},
            {'nome': 'Chambinho', 'preco': 2.50, 'estoque': 90, 'categoria': 'Kibon'},
            {'nome': 'Picolé Fruttare Coco', 'preco': 3.50, 'estoque': 70, 'categoria': 'Kibon'},
            {'nome': 'Cone Crocante Nestle', 'preco': 3.50, 'estoque': 85, 'categoria': 'Nestle'},
            {'nome': 'Cone KitKat', 'preco': 4.00, 'estoque': 60, 'categoria': 'Nestle'},
            {'nome': 'Cornetto Crocante', 'preco': 3.75, 'estoque': 75, 'categoria': 'Nestle'},
            {'nome': 'Cornetto M&Ms', 'preco': 4.25, 'estoque': 50, 'categoria': 'Nestle'},
            {'nome': 'Sorvete Magnum', 'preco': 5.00, 'estoque': 40, 'categoria': 'Nestle'},
            {'nome': 'Brigadeiro', 'preco': 1.50, 'estoque': 200, 'categoria': 'Kibon'},
            {'nome': 'Frutilly', 'preco': 2.50, 'estoque': 110, 'categoria': 'Italia'},
            {'nome': 'Sorvete Premium Italia', 'preco': 4.50, 'estoque': 55, 'categoria': 'Italia'},
            {'nome': 'Gelo Seco (kg)', 'preco': 15.00, 'estoque': 30, 'categoria': 'Gelo'},
            {'nome': 'Sacola Termica', 'preco': 8.00, 'estoque': 25, 'categoria': 'Acessorios'},
            {'nome': 'Caixa de Isopor', 'preco': 12.00, 'estoque': 20, 'categoria': 'Acessorios'},
            {'nome': 'Leite Moca', 'preco': 2.00, 'estoque': 150, 'categoria': 'Outros'},
        ]
        
        for prod_data in produtos_dados:
            prod = Produto.query.filter_by(nome=prod_data['nome']).first()
            if not prod:
                cat = categorias_dict.get(prod_data['categoria'])
                prod = Produto(
                    nome=prod_data['nome'],
                    preco=prod_data['preco'],
                    estoque=prod_data['estoque'],
                    categoria_id=cat.id if cat else None,
                    active=True
                )
                db.session.add(prod)
                print("  [OK] Produto {} criado".format(prod_data['nome']))
        
        db.session.commit()
        
        # 4. Criar clientes/ambulantes
        print("[SETUP] Criando clientes...")
        clientes_dados = [
            {'nome': 'Ivan Magé', 'telefone': '21999999999'},
            {'nome': 'João Silva', 'telefone': '21998888888'},
            {'nome': 'Maria Santos', 'telefone': '21997777777'},
        ]
        
        for cli_data in clientes_dados:
            cli = Cliente.query.filter_by(nome=cli_data['nome']).first()
            if not cli:
                cli = Cliente(
                    nome=cli_data['nome'],
                    telefone=cli_data['telefone'],
                    status='ativo'
                )
                db.session.add(cli)
                print("  [OK] Cliente {} criado".format(cli_data['nome']))
        
        db.session.commit()
        
        print("\n[SUCCESS] Banco de dados inicializado com sucesso!")
        print("  - Admin: admin / admin123")
        print("  - Categorias: 6 criadas")
        print("  - Produtos: 17 criados")
        print("  - Clientes: 3 criados")

if __name__ == '__main__':
    setup_database()
