from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Reutilizando a Base e db de vendedor.py ou definindo aqui se for o primeiro modelo
# Para evitar import circular e garantir que db seja o mesmo, idealmente db é inicializado em main.py e importado aqui.
# Assumindo por agora que db pode ser re-declarado ou importado de um arquivo central de modelos.

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base) # Esta linha seria idealmente uma importação

class Produto(db.Model):
    __tablename__ = "produto"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False) # Ex: "Picolé Kibon Chicabon"
    preco_venda = db.Column(db.Numeric(10, 2), nullable=False) # Preço que o vendedor paga por unidade vendida
    estoque = db.Column(db.Integer, nullable=False, default=0) # Quantidade atual em estoque
    # Adicionaremos relacionamentos com ItemPedido posteriormente
    # itens_pedido = db.relationship("ItemPedido", backref="produto", lazy=True)

    def __repr__(self):
        return f'<Produto {self.nome}>'
