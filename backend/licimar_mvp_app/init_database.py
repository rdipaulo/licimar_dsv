#!/usr/bin/env python3
"""
Script para inicializar o banco de dados do sistema Licimar
"""
import os
import sys

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import create_app
from src.database import db
from src.models import User, Categoria, Ambulante, RegraCobranca, Produto

def init_database():
    """
    Inicializa o banco de dados com dados padrão
    """
    app = create_app('development')
    
    with app.app_context():
        print("Criando tabelas...")
        db.create_all()
        
        # Cria usuário admin padrão
        print("Criando usuário administrador...")
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@licimar.com',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            print("✓ Usuário admin criado (login: admin / senha: admin123)")
        else:
            print("✓ Usuário admin já existe")
        
        # Cria categorias padrão
        print("Criando categorias padrão...")
        categorias_padrao = [
            {'nome': 'Kibon', 'descricao': 'Produtos da marca Kibon'},
            {'nome': 'Nestle', 'descricao': 'Produtos da marca Nestlé'},
            {'nome': 'Italia', 'descricao': 'Produtos da marca Itália'},
            {'nome': 'Gelo', 'descricao': 'Gelo seco e derivados'},
            {'nome': 'Acessórios', 'descricao': 'Acessórios diversos'},
            {'nome': 'Outros', 'descricao': 'Outros produtos'}
        ]
        
        categorias_criadas = 0
        for cat_data in categorias_padrao:
            if not Categoria.query.filter_by(nome=cat_data['nome']).first():
                categoria = Categoria(**cat_data)
                db.session.add(categoria)
                categorias_criadas += 1
        
        if categorias_criadas > 0:
            print(f"✓ {categorias_criadas} categorias criadas")
        else:
            print("✓ Categorias já existem")
        
        # Cria ambulantes padrão
        print("Criando ambulantes padrão...")
        ambulantes_padrao = [
            {'nome': 'Ivan Magé', 'email': 'ivan@licimar.com', 'telefone': '11987654321'},
            {'nome': 'Roberto Peixoto', 'email': 'roberto@licimar.com', 'telefone': '11912345678'},
            {'nome': 'Sabino', 'email': 'sabino@licimar.com', 'telefone': '11998765432'}
        ]
        
        ambulantes_criados = 0
        for amb_data in ambulantes_padrao:
            if not Ambulante.query.filter_by(nome=amb_data['nome']).first():
                ambulante = Ambulante(**amb_data)
                db.session.add(ambulante)
                ambulantes_criados += 1
        
        if ambulantes_criados > 0:
            print(f"✓ {ambulantes_criados} ambulantes criados")
        else:
            print("✓ Ambulantes já existem")
        
        # Cria regras de cobrança padrão
        print("Criando regras de cobrança padrão...")
        if not RegraCobranca.query.first():
            regras_padrao = [
                {'faixa_inicial': 0, 'faixa_final': 100, 'percentual': 20, 'descricao': 'Até R$ 100 - 20% de desconto'},
                {'faixa_inicial': 101, 'faixa_final': 300, 'percentual': 15, 'descricao': 'R$ 101 a R$ 300 - 15% de desconto'},
                {'faixa_inicial': 301, 'faixa_final': 999999, 'percentual': 10, 'descricao': 'Acima de R$ 300 - 10% de desconto'}
            ]
            
            for regra_data in regras_padrao:
                regra = RegraCobranca(**regra_data)
                db.session.add(regra)
            
            print(f"✓ {len(regras_padrao)} regras de cobrança criadas")
        else:
            print("✓ Regras de cobrança já existem")
        
        # Cria produtos padrão
        print("Criando produtos padrão...")
        if not Produto.query.first():
            # Busca categorias para associar aos produtos
            cat_kibon = Categoria.query.filter_by(nome='Kibon').first()
            cat_nestle = Categoria.query.filter_by(nome='Nestle').first()
            cat_italia = Categoria.query.filter_by(nome='Italia').first()
            cat_gelo = Categoria.query.filter_by(nome='Gelo').first()
            cat_acessorios = Categoria.query.filter_by(nome='Acessórios').first()
            cat_outros = Categoria.query.filter_by(nome='Outros').first()
            
            produtos_padrao = [
                # Kibon
                {'nome': 'Picolé Chicabon', 'preco': 8.00, 'estoque': 100, 'categoria_id': cat_kibon.id if cat_kibon else None, 'imagem_url': '/assets/images/chicabon.avif'},
                {'nome': 'Picolé Chicabon Zero', 'preco': 8.50, 'estoque': 80, 'categoria_id': cat_kibon.id if cat_kibon else None, 'imagem_url': '/assets/images/chicabon_zero.avif'},
                {'nome': 'Eskibon Clássico', 'preco': 9.00, 'estoque': 70, 'categoria_id': cat_kibon.id if cat_kibon else None, 'imagem_url': '/assets/images/eskibon_classico.avif'},
                {'nome': 'Chambinho', 'preco': 6.00, 'estoque': 120, 'categoria_id': cat_kibon.id if cat_kibon else None, 'imagem_url': '/assets/images/chambinho.jpeg'},
                {'nome': 'Picolé Fruttare Coco', 'preco': 6.50, 'estoque': 90, 'categoria_id': cat_kibon.id if cat_kibon else None, 'imagem_url': '/assets/images/fruttare_coco.avif'},
                
                # Nestlé
                {'nome': 'Cone Crocante Nestlé', 'preco': 12.00, 'estoque': 60, 'categoria_id': cat_nestle.id if cat_nestle else None, 'imagem_url': '/assets/images/cone_crocante_nestle.jpeg'},
                {'nome': 'Cone KitKat', 'preco': 14.00, 'estoque': 45, 'categoria_id': cat_nestle.id if cat_nestle else None, 'imagem_url': '/assets/images/cone_kitkat.jpeg'},
                {'nome': 'Cornetto Crocante', 'preco': 13.00, 'estoque': 50, 'categoria_id': cat_nestle.id if cat_nestle else None, 'imagem_url': '/assets/images/cornetto_crocante.avif'},
                {'nome': 'Cornetto M&Ms', 'preco': 15.00, 'estoque': 40, 'categoria_id': cat_nestle.id if cat_nestle else None, 'imagem_url': '/assets/images/cornetto_mms.avif'},
                {'nome': 'Sorvete Magnum', 'preco': 17.00, 'estoque': 50, 'categoria_id': cat_nestle.id if cat_nestle else None, 'imagem_url': '/assets/images/magnum_amendoas.jpeg'},
                
                # Itália
                {'nome': 'Brigadeiro', 'preco': 10.00, 'estoque': 65, 'categoria_id': cat_italia.id if cat_italia else None, 'imagem_url': '/assets/images/brigadeiro.avif'},
                {'nome': 'Frutilly', 'preco': 8.50, 'estoque': 75, 'categoria_id': cat_italia.id if cat_italia else None, 'imagem_url': '/assets/images/frutilly.avif'},
                {'nome': 'Sorvete Premium Itália', 'preco': 11.00, 'estoque': 35, 'categoria_id': cat_italia.id if cat_italia else None, 'imagem_url': '/assets/images/premium_italia.jpeg'},
                
                # Gelo
                {'nome': 'Gelo Seco (kg)', 'preco': 28.00, 'estoque': 200, 'categoria_id': cat_gelo.id if cat_gelo else None, 'imagem_url': '/assets/images/gelo_seco.jpeg'},
                
                # Acessórios
                {'nome': 'Sacola Térmica', 'preco': 5.00, 'estoque': 50, 'categoria_id': cat_acessorios.id if cat_acessorios else None, 'imagem_url': '/assets/images/sacola_termica.jpeg'},
                {'nome': 'Caixa de Isopor', 'preco': 15.00, 'estoque': 30, 'categoria_id': cat_acessorios.id if cat_acessorios else None, 'imagem_url': '/assets/images/caixa_isopor.jpeg'},
                
                # Outros
                {'nome': 'Leite Moça', 'preco': 9.50, 'estoque': 60, 'categoria_id': cat_outros.id if cat_outros else None, 'imagem_url': '/assets/images/leite_moca.jpeg'},
            ]
            
            for produto_data in produtos_padrao:
                produto = Produto(**produto_data)
                db.session.add(produto)
            
            print(f"✓ {len(produtos_padrao)} produtos criados")
        else:
            print("✓ Produtos já existem")
        
        # Commit todas as alterações
        db.session.commit()
        
        print("\n" + "="*50)
        print("BANCO DE DADOS INICIALIZADO COM SUCESSO!")
        print("="*50)
        print("\nPara acessar o sistema:")
        print("1. Execute: python src/main.py")
        print("2. Acesse: http://localhost:5000")
        print("3. Login: admin")
        print("4. Senha: admin123")
        print("\nAPI disponível em: http://localhost:5000/api/")

if __name__ == '__main__':
    init_database()
