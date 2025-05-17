from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

# Importar os modelos para que sejam registrados com SQLAlchemy e para facilitar o acesso
# Certifique-se de que os arquivos dos modelos existam e estejam corretos.
from .vendedor import Vendedor
from .produto import Produto
from .pedido import Pedido
from .item_pedido import ItemPedido

