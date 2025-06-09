from src.database import db
from datetime import datetime

class Vendedor(db.Model):
    __tablename__ = "vendedores"
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    active = db.Column(db.Boolean, nullable=False, default=True)

    # Relacionamento com Pedidos (um vendedor pode ter vários pedidos)
    pedidos = db.relationship('Pedido', backref='vendedor', lazy=True)

    def __repr__(self):
        return f'<Vendedor {self.nome}>'
