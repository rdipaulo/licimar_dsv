#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simples script para inicializar banco de dados"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import create_app
from src.database import db
from src.models import (User, Categoria, Ambulante, RegraCobranca, Produto)

def init():
    """Inicializa banco de dados"""
    app = create_app('development')
    
    with app.app_context():
        print("Criando tabelas...")
        db.create_all()
        print("OK - Tabelas criadas")
        
        # Admin
        print("Criando usuario admin...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@licimar.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("OK - Usuário admin criado")
        else:
            print("OK - Usuario admin ja existe")
        
        # Categorias
        print("Criando categorias...")
        categorias = [
            {'nome': 'Kibon', 'descricao': 'Produtos Kibon'},
            {'nome': 'Nestle', 'descricao': 'Produtos Nestle'},
            {'nome': 'Italia', 'descricao': 'Produtos Italia'},
            {'nome': 'Gelo', 'descricao': 'Gelo seco'},
            {'nome': 'Acessorios', 'descricao': 'Acessorios'},
            {'nome': 'Outros', 'descricao': 'Outros'},
        ]
        for cat_data in categorias:
            cat = Categoria.query.filter_by(nome=cat_data['nome']).first()
            if not cat:
                cat = Categoria(nome=cat_data['nome'], descricao=cat_data['descricao'])
                db.session.add(cat)
                print("OK - Categoria {} criada".format(cat_data['nome']))
        
        # Ambulantes
        print("Criando ambulantes...")
        ambulantes = [
            {'nome': 'Ivan Magé', 'telefone': '21999999999'},
            {'nome': 'João Silva', 'telefone': '21998888888'},
            {'nome': 'Maria Santos', 'telefone': '21997777777'},
        ]
        for amb_data in ambulantes:
            amb = Ambulante.query.filter_by(nome=amb_data['nome']).first()
            if not amb:
                amb = Ambulante(nome=amb_data['nome'], telefone=amb_data['telefone'], status='ativo')
                db.session.add(amb)
                print("OK - Ambulante {} criado".format(amb_data['nome']))
        
        db.session.commit()
        print("\nBanco de dados inicializado com sucesso!")

if __name__ == '__main__':
    init()
