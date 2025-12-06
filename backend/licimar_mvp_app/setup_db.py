#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 SETUP UNIFICADO - Database Initialization Script
Este é o ÚNICO script de setup do banco de dados.
Mantém todas as 12 tabelas em sincronização.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/licimar_mvp_app'))

from src.main import create_app
from src.database import db
from src.models import (
    User, Categoria, Cliente, Produto, RegraCobranca,
    Pedido, ItemPedido, Log,
    Divida, PagamentoDivida, PedidoConsignacao, ItemPedidoConsignacao
)

def setup_database():
    """Setup banco de dados - inicializa todas as 12 tabelas"""
    app = create_app('development')
    
    with app.app_context():
        print("\n" + "="*70)
        print("🚀 INICIANDO SETUP UNIFICADO DO BANCO DE DADOS")
        print("="*70 + "\n")
        
        print("[1/8] Criando todas as 12 tabelas...")
        db.create_all()
        print("  ✅ Tabelas criadas/verificadas\n")
        
        # 1. Criar usuário admin
        print("[2/8] Configurando usuários...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@licimar.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("  ✅ Admin criado (login: admin / senha: admin123)")
        else:
            print("  ✅ Admin já existe")
        
        db.session.commit()
        
        # 2. Criar categorias
        print("\n[3/8] Configurando categorias (6)...")
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
                print(f"  ✅ Categoria '{cat_data['nome']}' criada")
            categorias_dict[cat_data['nome']] = cat
        
        db.session.commit()
        
        # 3. Criar produtos (17)
        print("\n[4/8] Configurando produtos (17)...")
        produtos_dados = [
            {'nome': 'Picolé Chicabon', 'preco': 2.50, 'estoque': 100, 'categoria': 'Kibon', 'nao_devolve': False},
            {'nome': 'Picolé Chicabon Zero', 'preco': 3.00, 'estoque': 80, 'categoria': 'Kibon', 'nao_devolve': False},
            {'nome': 'Eskibon Classico', 'preco': 2.75, 'estoque': 120, 'categoria': 'Kibon', 'nao_devolve': False},
            {'nome': 'Chambinho', 'preco': 2.50, 'estoque': 90, 'categoria': 'Kibon', 'nao_devolve': False},
            {'nome': 'Picolé Fruttare Coco', 'preco': 3.50, 'estoque': 70, 'categoria': 'Kibon', 'nao_devolve': False},
            {'nome': 'Cone Crocante Nestle', 'preco': 3.50, 'estoque': 85, 'categoria': 'Nestle', 'nao_devolve': False},
            {'nome': 'Cone KitKat', 'preco': 4.00, 'estoque': 60, 'categoria': 'Nestle', 'nao_devolve': False},
            {'nome': 'Cornetto Crocante', 'preco': 3.75, 'estoque': 75, 'categoria': 'Nestle', 'nao_devolve': False},
            {'nome': 'Cornetto M&Ms', 'preco': 4.25, 'estoque': 50, 'categoria': 'Nestle', 'nao_devolve': False},
            {'nome': 'Sorvete Magnum', 'preco': 5.00, 'estoque': 40, 'categoria': 'Nestle', 'nao_devolve': False},
            {'nome': 'Brigadeiro', 'preco': 1.50, 'estoque': 200, 'categoria': 'Kibon', 'nao_devolve': False},
            {'nome': 'Frutilly', 'preco': 2.50, 'estoque': 110, 'categoria': 'Italia', 'nao_devolve': False},
            {'nome': 'Sorvete Premium Italia', 'preco': 4.50, 'estoque': 55, 'categoria': 'Italia', 'nao_devolve': False},
            {'nome': 'Gelo Seco (kg)', 'preco': 15.00, 'estoque': 30, 'categoria': 'Gelo', 'nao_devolve': True},
            {'nome': 'Sacola Termica', 'preco': 8.00, 'estoque': 25, 'categoria': 'Acessorios', 'nao_devolve': True},
            {'nome': 'Caixa de Isopor', 'preco': 12.00, 'estoque': 20, 'categoria': 'Acessorios', 'nao_devolve': True},
            {'nome': 'Leite Moca', 'preco': 2.00, 'estoque': 150, 'categoria': 'Outros', 'nao_devolve': False},
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
                    active=True,
                    nao_devolve=prod_data.get('nao_devolve', False)
                )
                db.session.add(prod)
                print(f"  ✅ Produto '{prod_data['nome']}' criado (nao_devolve={prod_data.get('nao_devolve', False)})")
            else:
                # ATUALIZAR produtos existentes com flag nao_devolve
                prod.nao_devolve = prod_data.get('nao_devolve', False)
        
        db.session.commit()
        
        # 4. Criar clientes (3)
        print("\n[5/8] Configurando clientes (3)...")
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
                print(f"  ✅ Cliente '{cli_data['nome']}' criado")
        
        db.session.commit()
        
        # 5. Criar Regras de Cobrança
        print("\n[6/8] Configurando regras de cobrança...")
        regras = [
            {'faixa_inicial': 0, 'faixa_final': 50, 'percentual': 0},
            {'faixa_inicial': 50.01, 'faixa_final': 100, 'percentual': 2},
            {'faixa_inicial': 100.01, 'faixa_final': 500, 'percentual': 5},
            {'faixa_inicial': 500.01, 'faixa_final': 9999, 'percentual': 10},
        ]
        
        for regra_data in regras:
            regra = RegraCobranca.query.filter_by(
                faixa_inicial=regra_data['faixa_inicial'],
                faixa_final=regra_data['faixa_final']
            ).first()
            if not regra:
                regra = RegraCobranca(
                    faixa_inicial=regra_data['faixa_inicial'],
                    faixa_final=regra_data['faixa_final'],
                    percentual=regra_data['percentual'],
                    descricao=f"Faixa R$ {regra_data['faixa_inicial']:.2f} a R$ {regra_data['faixa_final']:.2f}",
                    active=True
                )
                db.session.add(regra)
                print(f"  ✅ Regra criada: R$ {regra_data['faixa_inicial']:.2f} a R$ {regra_data['faixa_final']:.2f} ({regra_data['percentual']}%)")
        
        db.session.commit()
        
        # 6. Criar Dívidas de exemplo (relacionadas aos clientes)
        print("\n[7/8] Configurando dívidas de exemplo...")
        clientes = Cliente.query.all()
        if len(clientes) >= 1:
            divida1 = Divida.query.filter_by(id_cliente=clientes[0].id).first()
            if not divida1:
                divida1 = Divida(
                    id_cliente=clientes[0].id,
                    valor_divida=250.50,
                    descricao="Dívida acumulada de saídas anteriores",
                    status="Em Aberto"
                )
                db.session.add(divida1)
                print(f"  ✅ Dívida criada para {clientes[0].nome}: R$ 250.50")
        
        db.session.commit()
        
        # 7. Verificar integridade do banco
        print("\n[8/8] Verificando integridade do banco...")
        
        # Contar registros em cada tabela
        total_usuarios = db.session.query(User).count()
        total_categorias = db.session.query(Categoria).count()
        total_produtos = db.session.query(Produto).count()
        total_clientes = db.session.query(Cliente).count()
        total_regras = db.session.query(RegraCobranca).count()
        total_dividas = db.session.query(Divida).count()
        
        print(f"  ✅ Usuários: {total_usuarios}")
        print(f"  ✅ Categorias: {total_categorias}")
        print(f"  ✅ Produtos: {total_produtos}")
        print(f"  ✅ Clientes: {total_clientes}")
        print(f"  ✅ Regras de Cobrança: {total_regras}")
        print(f"  ✅ Dívidas: {total_dividas}")
        
        print("\n" + "="*70)
        print("✅ SETUP CONCLUÍDO COM SUCESSO!")
        print("="*70)
        print("\n📊 RESUMO:")
        print(f"  - Tabelas: 12 (todas criadas e sincronizadas)")
        print(f"  - Usuários: {total_usuarios}")
        print(f"  - Categorias: {total_categorias}")
        print(f"  - Produtos: {total_produtos}")
        print(f"  - Clientes: {total_clientes}")
        print(f"  - Regras: {total_regras}")
        print(f"  - Dívidas: {total_dividas}")
        print("\n🔐 Credenciais:")
        print("  - User: admin")
        print("  - Pass: admin123")
        print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    setup_database()
