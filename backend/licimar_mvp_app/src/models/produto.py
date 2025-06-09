from src.database import db
from datetime import datetime

class Produto(db.Model):
    __tablename__ = "produtos"
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    # Usar Numeric para precisão decimal em preços
    preco_venda = db.Column(db.Numeric(10, 2), nullable=False)
    estoque = db.Column(db.Integer, nullable=False, default=0)
    imagem_url = db.Column(db.String(255), nullable=True)
    descricao = db.Column(db.Text, nullable=True)
    categoria = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    active = db.Column(db.Boolean, nullable=False, default=True)

    # Relacionamento com Itens de Pedido
    itens_pedido = db.relationship('ItemPedido', backref='produto', lazy=True)

    def __repr__(self):
        return f'<Produto {self.nome}>'
