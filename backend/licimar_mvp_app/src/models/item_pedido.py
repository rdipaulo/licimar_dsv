from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# Assumindo que db será importado de um local centralizado (ex: main.py ou models/__init__.py)
# from . import db # Exemplo se db estivesse em models/__init__.py
# Por agora, para desenvolvimento isolado do arquivo:
class Base(DeclarativeBase):
  pass
db = SQLAlchemy(model_class=Base)

class ItemPedido(db.Model):
    __tablename__ = "item_pedido"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False)
    
    quantidade_saida = db.Column(db.Integer, nullable=False, default=0)
    quantidade_retorno = db.Column(db.Integer, nullable=False, default=0) # Retorno em bom estado
    quantidade_perda = db.Column(db.Integer, nullable=False, default=0) # Produto estragado/avariado
    
    preco_venda_unitario_registrado = db.Column(db.Numeric(10, 2), nullable=False) # Preço do produto no momento da saída

    # Relacionamento com Pedido (se definido em Pedido.py)
    # pedido = relationship("Pedido", back_populates="itens_pedido")
    # Relacionamento com Produto (se definido em Produto.py)
    # produto = relationship("Produto", back_populates="itens_pedido")

    def __repr__(self):
        return f'<ItemPedido {self.id} - Pedido {self.pedido_id} - Produto {self.produto_id}>'
