# Salve como check_admin.py
import os
import sys
from flask import Flask

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__ )))
from src.database import db
from src.models.user import User

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'licimar.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"Usuário admin encontrado! ID: {admin.id}, Email: {admin.email}")
    else:
        print("Usuário admin NÃO encontrado!")
