
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import config
from .database import db, migrate
from .models import *
from .routes.auth import auth_bp
from .routes.ambulantes import ambulantes_bp
from .routes.produtos import produtos_bp
from .routes.categorias import categorias_bp
from .routes.regras_cobranca import regras_cobranca_bp
from .routes.usuarios import usuarios_bp
from .routes.pedidos import pedidos_bp
from .routes.relatorios import relatorios_bp
from .routes.logs import logs_bp

def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Garante que o diretório da instância exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token expirado'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'message': 'Token inválido'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'message': 'Token de autorização requerido'}), 401

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(ambulantes_bp, url_prefix='/api/ambulantes')
    app.register_blueprint(produtos_bp, url_prefix='/api/produtos')
    app.register_blueprint(categorias_bp, url_prefix='/api/categorias')
    app.register_blueprint(regras_cobranca_bp, url_prefix='/api/regras-cobranca')
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
    app.register_blueprint(pedidos_bp, url_prefix='/api/pedidos')
    app.register_blueprint(relatorios_bp, url_prefix='/api/relatorios')
    app.register_blueprint(logs_bp, url_prefix='/api/logs')

    @app.route('/')
    def index():
        return jsonify({
            'message': 'API Licimar - Sistema de Gestão de Ambulantes',
            'version': '2.0.0',
            'status': 'online',
            'environment': config_name
        })

    @app.route('/api/status')
    def api_status():
        return jsonify({
            'status': 'online',
            'message': 'API Licimar funcionando corretamente',
            'version': '2.0.0',
            'environment': config_name
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Endpoint não encontrado'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'message': 'Erro interno do servidor'}), 500

    return app
