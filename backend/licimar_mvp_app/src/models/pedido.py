from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import datetime

# Assumindo que db será importado de um local centralizado (ex: main.py ou models/__init__.py)
# from . import db # Exemplo se db estivesse em models/__init__.py
# Por agora, para desenvolvimento isolado do arquivo:
class Base(DeclarativeBase):
  pass
db = SQLAlchemy(model_class=Base)

class Pedido(db.Model):
    __tablename__ = "pedido"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vendedor_id = db.Column(db.Integer, db.ForeignKey("vendedor.id"), nullable=False)
    data_operacao = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default="EM_ABERTO") # Ex: EM_ABERTO, FECHADO
    valor_total_a_pagar = db.Column(db.Numeric(10, 2), nullable=True) # Calculado no fechamento

    # Relacionamento com Vendedor (se definido em Vendedor.py)
    # vendedor = relationship("Vendedor", back_populates="pedidos")
    # Relacionamento com ItemPedido
    # itens_pedido = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Pedido {self.id} - Vendedor {self.vendedor_id} - Status {self.status}>'

