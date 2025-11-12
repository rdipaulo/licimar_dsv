import os
from src.main import create_app
from src.database import db
from src.models import User, Ambulante, Categoria, Produto, RegraCobranca

# Define o ambiente para desenvolvimento
os.environ['FLASK_ENV'] = 'development'

# Cria o diretório 'instance' se não existir
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

app = create_app()

with app.app_context():
    print("Populando o banco de dados com dados de teste...")

    # Criar usuário administrador
    admin_user = User(username='admin', email='admin@example.com', role='admin')
    admin_user.set_password('admin123')
    db.session.add(admin_user)

    # Criar categoria
    categoria = Categoria(nome='Alimentos', descricao='Produtos alimentícios em geral')
    db.session.add(categoria)

    # Criar ambulante
    ambulante = Ambulante(nome='João da Silva', cpf='123.456.789-00', telefone='(11) 98765-4321', email='joao.silva@example.com', endereco='Em frente ao portão principal')
    db.session.add(ambulante)

    # Criar produto
    produto = Produto(nome='Cachorro-Quente', descricao='Pão, salsicha, purê, batata palha', preco=10.0, categoria_id=1, estoque=50)
    db.session.add(produto)

    # Criar regra de cobrança
    regra = RegraCobranca(faixa_inicial=0, faixa_final=100, percentual=10)
    db.session.add(regra)

    db.session.commit()

    print("Banco de dados populado com sucesso!")
