from src.database import db
from datetime import datetime

class ItemPedido(db.Model):
    __tablename__ = "itens_pedido"
    
    id = db.Column(db.Integer, primary_key=True)
    # Chave estrangeira para Pedido
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    # Chave estrangeira para Produto
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade_saida = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    quantidade_retorno = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    quantidade_perda = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    preco_venda_unitario_registrado = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<ItemPedido {self.id} - Pedido {self.pedido_id} - Produto {self.produto_id}>'
