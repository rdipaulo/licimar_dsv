"""
Configuração e inicialização do banco de dados
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instância do SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """
    Inicializa o banco de dados com a aplicação Flask
    """
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Criar tabelas se não existirem
    with app.app_context():
        db.create_all()

def create_tables():
    """
    Cria todas as tabelas do banco de dados
    """
    db.create_all()

def drop_tables():
    """
    Remove todas as tabelas do banco de dados
    """
    db.drop_all()

def reset_database():
    """
    Reseta o banco de dados (remove e recria todas as tabelas)
    """
    drop_tables()
    create_tables()
