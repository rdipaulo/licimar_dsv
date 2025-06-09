import os
import sys
from werkzeug.security import generate_password_hash
from flask import Flask

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importa o necessário
from src.database import db
from src.models.user import User

# Cria uma aplicação Flask mínima
app = Flask(__name__)
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'licimar.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Cria o usuário admin
with app.app_context():
    if User.query.filter_by(username='admin').first() is None:
        admin = User(
            username="admin",
            email="admin@licimar.com",
            password_hash=generate_password_hash("admin123"),
            role="admin",
            active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Usuário admin criado com sucesso!")
    else:
        print("Usuário admin já existe!")
