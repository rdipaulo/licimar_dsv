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
    Cria as tabelas do banco de dados.
    """
    with app.app_context():
        db.drop_all()
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
