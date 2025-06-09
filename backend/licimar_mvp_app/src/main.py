import os
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
from functools import wraps

import os
import sys

# Adiciona o diretório raiz do projeto ao path do Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa a função de inicialização do DB e a instância db
from database import db, init_db
# Importa todos os modelos
from models import * 
# Importa funções auxiliares e decorators
from utils.helpers import register_log
from src.utils.decorators import token_required, role_required

# Importa os blueprints
from src.routes.auth import auth_bp
from src.routes.produtos import produtos_bp
from src.routes.vendedores import vendedores_bp
from src.routes.pedidos import pedidos_bp
from src.routes.logs import logs_bp

# Função para criar a aplicação Flask (Factory Pattern)
def create_app(config_overrides=None):
    app = Flask(__name__) 
    # Configurações padrão
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'uma-chave-secreta-muito-forte'), # Mude isso em produção!
        JWT_EXPIRATION_DAYS=1 # Define a duração do token (1 dia)
    )

    # Permite sobrescrever configurações (útil para testes)
    if config_overrides:
        app.config.update(config_overrides)

    # Configura CORS para permitir requisições do frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}}) # Ajuste as origins em produção

    # Inicializa o banco de dados com a aplicação
    init_db(app)

    # --- Registro das Rotas (Blueprints) --- 
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(produtos_bp, url_prefix="/api/produtos")
    app.register_blueprint(vendedores_bp, url_prefix="/api/vendedores")
    app.register_blueprint(pedidos_bp, url_prefix="/api/pedidos")
    app.register_blueprint(logs_bp, url_prefix="/api/logs")

    # Rota de teste inicial
    @app.route('/')
    def index():
        return jsonify({"message": "Bem-vindo à API Licimar!"})

    return app

# Ponto de entrada para execução direta (python src/main.py)
if __name__ == '__main__':
    app = create_app()
    # Roda o servidor Flask em modo de desenvolvimento
    # host='0.0.0.0' permite acesso de outras máquinas na rede
    # debug=True ativa o modo de depuração (recarrega automaticamente, mostra erros detalhados)
    # Use debug=False em produção!
    app.run(host='0.0.0.0', port=5000, debug=True)
