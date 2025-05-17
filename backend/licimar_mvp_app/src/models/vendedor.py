from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

class Vendedor(db.Model):
    __tablename__ = "vendedor"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), unique=True, nullable=False) # Nome do vendedor, para identificação
    # Adicionaremos relacionamentos com Pedido posteriormente, se necessário para o MVP
    # pedidos = db.relationship('Pedido', backref='vendedor', lazy=True)

    def __repr__(self):
        return f'<Vendedor {self.nome}>'
