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
            {'nome': 'Picolés', 'descricao': 'Picolés diversos'},
            {'nome': 'Sorvetes Premium', 'descricao': 'Sorvetes premium e especiais'},
            {'nome': 'Picolés de Fruta', 'descricao': 'Picolés de frutas naturais'},
            {'nome': 'Cones', 'descricao': 'Sorvetes em cone'},
            {'nome': 'Sorvetes de Leite', 'descricao': 'Sorvetes cremosos'},
            {'nome': 'Chocolates', 'descricao': 'Chocolates e bombons'},
            {'nome': 'Doces', 'descricao': 'Balas e doces diversos'},
            {'nome': 'Especiais', 'descricao': 'Produtos especiais'},
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
            cat_picoles = Categoria.query.filter_by(nome='Picolés').first()
            cat_premium = Categoria.query.filter_by(nome='Sorvetes Premium').first()
            cat_frutas = Categoria.query.filter_by(nome='Picolés de Fruta').first()
            cat_cones = Categoria.query.filter_by(nome='Cones').first()
            cat_leite = Categoria.query.filter_by(nome='Sorvetes de Leite').first()
            cat_chocolates = Categoria.query.filter_by(nome='Chocolates').first()
            cat_doces = Categoria.query.filter_by(nome='Doces').first()
            cat_especiais = Categoria.query.filter_by(nome='Especiais').first()
            cat_outros = Categoria.query.filter_by(nome='Outros').first()
            
            produtos_padrao = [
                # Picolés
                {'nome': 'Picolé Chicabon', 'preco': 8.00, 'estoque': 100, 'categoria_id': cat_picoles.id if cat_picoles else None, 'imagem_url': '/assets/images/chicabon.avif'},
                {'nome': 'Picolé Chicabon Zero', 'preco': 8.50, 'estoque': 80, 'categoria_id': cat_picoles.id if cat_picoles else None, 'imagem_url': '/assets/images/chicabon_zero.avif'},
                {'nome': 'Eskibon Clássico', 'preco': 9.00, 'estoque': 70, 'categoria_id': cat_picoles.id if cat_picoles else None, 'imagem_url': '/assets/images/eskibon_classico.avif'},
                {'nome': 'Chambinho', 'preco': 6.00, 'estoque': 120, 'categoria_id': cat_picoles.id if cat_picoles else None, 'imagem_url': '/assets/images/chambinho.jpeg'},
                {'nome': 'Caribe', 'preco': 7.00, 'estoque': 100, 'categoria_id': cat_picoles.id if cat_picoles else None, 'imagem_url': '/assets/images/caribe.jpeg'},
                
                # Sorvetes Premium
                {'nome': 'Sorvete Magnum Amêndoas', 'preco': 17.00, 'estoque': 50, 'categoria_id': cat_premium.id if cat_premium else None, 'imagem_url': '/assets/images/magnum_amendoas.jpeg'},
                {'nome': 'Diamante Negro', 'preco': 11.00, 'estoque': 35, 'categoria_id': cat_premium.id if cat_premium else None, 'imagem_url': '/assets/images/diamante_negro.jpeg'},
                {'nome': 'Brigadeiro', 'preco': 10.00, 'estoque': 65, 'categoria_id': cat_premium.id if cat_premium else None, 'imagem_url': '/assets/images/brigadeiro.avif'},
                
                # Picolés de Fruta
                {'nome': 'Picolé Fruttare Morango', 'preco': 6.50, 'estoque': 120, 'categoria_id': cat_frutas.id if cat_frutas else None, 'imagem_url': '/assets/images/fruttare_morango.jpeg'},
                {'nome': 'Picolé Fruttare Abacaxi', 'preco': 6.50, 'estoque': 100, 'categoria_id': cat_frutas.id if cat_frutas else None, 'imagem_url': '/assets/images/fruttare_abacaxi.jpeg'},
                {'nome': 'Picolé Fruttare Coco', 'preco': 6.50, 'estoque': 90, 'categoria_id': cat_frutas.id if cat_frutas else None, 'imagem_url': '/assets/images/fruttare_coco.avif'},
                {'nome': 'Picolé Fruttare Limão', 'preco': 6.50, 'estoque': 110, 'categoria_id': cat_frutas.id if cat_frutas else None, 'imagem_url': '/assets/images/fruttare_limao.avif'},
                {'nome': 'Picolé Fruttare Uva', 'preco': 6.50, 'estoque': 95, 'categoria_id': cat_frutas.id if cat_frutas else None, 'imagem_url': '/assets/images/fruttare_uva.avif'},
                {'nome': 'Frutilly', 'preco': 8.50, 'estoque': 75, 'categoria_id': cat_frutas.id if cat_frutas else None, 'imagem_url': '/assets/images/frutilly.avif'},
                
                # Cones
                {'nome': 'Cone Crocante Nestlé', 'preco': 12.00, 'estoque': 60, 'categoria_id': cat_cones.id if cat_cones else None, 'imagem_url': '/assets/images/cone_crocante_nestle.jpeg'},
                {'nome': 'Cone KitKat', 'preco': 14.00, 'estoque': 45, 'categoria_id': cat_cones.id if cat_cones else None, 'imagem_url': '/assets/images/cone_kitkat.jpeg'},
                {'nome': 'Cornetto Brigadeiro', 'preco': 13.00, 'estoque': 55, 'categoria_id': cat_cones.id if cat_cones else None, 'imagem_url': '/assets/images/cornetto_brigadeiro.jpeg'},
                {'nome': 'Cornetto Crocante', 'preco': 13.00, 'estoque': 50, 'categoria_id': cat_cones.id if cat_cones else None, 'imagem_url': '/assets/images/cornetto_crocante.avif'},
                {'nome': 'Cornetto M&Ms', 'preco': 15.00, 'estoque': 40, 'categoria_id': cat_cones.id if cat_cones else None, 'imagem_url': '/assets/images/cornetto_mms.avif'},
                
                # Sorvetes de Leite
                {'nome': 'LaFrutta Coco', 'preco': 7.50, 'estoque': 85, 'categoria_id': cat_leite.id if cat_leite else None, 'imagem_url': '/assets/images/lafrutta_coco.jpeg'},
                {'nome': 'LaFrutta Manga', 'preco': 7.50, 'estoque': 80, 'categoria_id': cat_leite.id if cat_leite else None, 'imagem_url': '/assets/images/lafrutta_manga.jpeg'},
                {'nome': 'LaFrutta Maracujá com Leite', 'preco': 7.50, 'estoque': 75, 'categoria_id': cat_leite.id if cat_leite else None, 'imagem_url': '/assets/images/lafrutta_maracuja_leite.jpeg'},
                {'nome': 'LaFrutta Morango com Leite', 'preco': 7.50, 'estoque': 90, 'categoria_id': cat_leite.id if cat_leite else None, 'imagem_url': '/assets/images/lafrutta_morango_leite.jpeg'},
                
                # Chocolates
                {'nome': 'Baton', 'preco': 5.50, 'estoque': 150, 'categoria_id': cat_chocolates.id if cat_chocolates else None, 'imagem_url': '/assets/images/baton.jpeg'},
                {'nome': 'Bombom Garoto', 'preco': 4.50, 'estoque': 200, 'categoria_id': cat_chocolates.id if cat_chocolates else None, 'imagem_url': '/assets/images/bombom_garoto.jpeg'},
                {'nome': 'Laka Oreo', 'preco': 12.00, 'estoque': 40, 'categoria_id': cat_chocolates.id if cat_chocolates else None, 'imagem_url': '/assets/images/laka_oreo.jpeg'},
                
                # Doces
                {'nome': 'Fini Dentadura', 'preco': 3.50, 'estoque': 180, 'categoria_id': cat_doces.id if cat_doces else None, 'imagem_url': '/assets/images/fini_dentadura.jpeg'},
                {'nome': 'Fini Tube Morango', 'preco': 4.00, 'estoque': 160, 'categoria_id': cat_doces.id if cat_doces else None, 'imagem_url': '/assets/images/fini_tube_morango.jpeg'},
                {'nome': 'Fini Tube Tutti-Frutti', 'preco': 4.00, 'estoque': 160, 'categoria_id': cat_doces.id if cat_doces else None, 'imagem_url': '/assets/images/fini_tube_tuttifruti.jpeg'},
                
                # Especiais
                {'nome': 'Leite Moça', 'preco': 9.50, 'estoque': 60, 'categoria_id': cat_especiais.id if cat_especiais else None, 'imagem_url': '/assets/images/leite_moca.jpeg'},
                
                # Outros
                {'nome': 'Gelo Seco (kg)', 'preco': 28.00, 'estoque': 200, 'categoria_id': cat_outros.id if cat_outros else None, 'imagem_url': '/assets/images/gelo_seco.jpeg'},
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
