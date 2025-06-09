# backend/licimar_mvp_app/src/models/__init__.py
from .user import User
from .vendedor import Vendedor
from .produto import Produto
from .pedido import Pedido
from .item_pedido import ItemPedido
from .log import Log
from .configuracao import Configuracao

# Você pode definir __all__ se quiser controlar o que é importado com 'from .models import *'
__all__ = [
    'User', 'Vendedor', 'Produto', 'Pedido', 
    'ItemPedido', 'Log', 'Configuracao'
]
