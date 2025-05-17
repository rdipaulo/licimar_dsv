from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Criar uma nova instância do Flask
app = Flask(__name__)

# Configurar o banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'licimar.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar o SQLAlchemy
db = SQLAlchemy(app)

# Definir modelos diretamente neste arquivo para evitar problemas de importação

# Modelo Vendedor
class Vendedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f"<Vendedor {self.id} - {self.nome}>"

# Modelo Produto
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco_venda = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f"<Produto {self.id} - {self.nome}>"

# Modelo Pedido
class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedor.id'), nullable=False)
    data_operacao = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='saida')  # 'saida' ou 'retorno'
    
    def __repr__(self):
        return f"<Pedido {self.id} - Vendedor {self.vendedor_id} - Status {self.status}>"

# Modelo ItemPedido
class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade_saida = db.Column(db.Integer, default=0)
    quantidade_retorno = db.Column(db.Integer, default=0)
    quantidade_perda = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f"<ItemPedido {self.id} - Pedido {self.pedido_id} - Produto {self.produto_id}>"

# Criar o banco de dados
with app.app_context():
    db.create_all()
    
    # Adicionar alguns dados de exemplo
    # Vendedores
    if not Vendedor.query.first():
        vendedores = [
            Vendedor(nome="João Silva"),
            Vendedor(nome="Maria Oliveira"),
            Vendedor(nome="Carlos Santos")
        ]
        db.session.add_all(vendedores)
    
    # Produtos
    if not Produto.query.first():
        produtos = [
            Produto(nome="Picolé Chocolate", preco_venda=5.0, estoque=100),
            Produto(nome="Picolé Morango", preco_venda=5.0, estoque=80),
            Produto(nome="Sorvete Napolitano", preco_venda=15.0, estoque=50),
            Produto(nome="Gelo Seco (kg)", preco_venda=8.0, estoque=200)
        ]
        db.session.add_all(produtos)
    
    db.session.commit()
    print("Banco de dados criado com sucesso e dados de exemplo adicionados!")
