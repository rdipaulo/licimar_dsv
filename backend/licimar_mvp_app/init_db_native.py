import sqlite3
import os
from src.main import create_app
from src.database import db

# Define o ambiente para desenvolvimento
os.environ['FLASK_ENV'] = 'development'

app = create_app()

with app.app_context():
    # Caminho absoluto para o diretório da instância
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # Caminho para o arquivo do banco de dados
    db_path = os.path.join(instance_path, 'licimar_dev.db')
    
    print(f"Tentando criar o banco de dados em: {db_path}")
    
    conn = None
    try:
        # Conecta ao banco de dados (o arquivo será criado se não existir)
        conn = sqlite3.connect(db_path)
        print(f'Conexão com o banco de dados {db_path} bem-sucedida.')
        
        # Fecha a conexão para que o SQLAlchemy possa usá-lo
        conn.close()
        
        # Usa o SQLAlchemy para criar as tabelas no banco de dados já existente
        print("Criando tabelas com SQLAlchemy...")
        db.drop_all()
        db.create_all()
        print("Tabelas criadas com sucesso.")
        
    except sqlite3.Error as e:
        print(f'Ocorreu um erro no SQLite: {e}')
    except Exception as e:
        print(f'Ocorreu um erro ao usar SQLAlchemy: {e}')
    finally:
        if conn:
            conn.close()
