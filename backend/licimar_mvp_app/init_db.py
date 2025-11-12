import os
from src.main import create_app
from src.database import init_db

# Define o ambiente para desenvolvimento
os.environ['FLASK_ENV'] = 'development'

app = create_app()

# Garante que o diretório 'instance' exista
instance_path = os.path.join(app.root_path, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

with app.app_context():
    print("URI do Banco de Dados:", app.config['SQLALCHEMY_DATABASE_URI'])
    print("Inicializando o banco de dados...")
    init_db(app)
    print("Banco de dados inicializado com sucesso.")
