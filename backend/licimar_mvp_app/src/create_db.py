import sys
import os

# Adicionar o diretório atual ao path do Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from models import db

# Garantir que o app está no contexto correto
with app.app_context():
    db.create_all()
    print("Banco de dados criado com sucesso!")
