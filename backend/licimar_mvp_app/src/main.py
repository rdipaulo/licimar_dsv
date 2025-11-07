"""
Aplicação principal Flask para o sistema Licimar
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from database import db, init_db
from models import *  # Importa todos os modelos

# Importa todos os blueprints
from routes.auth import auth_bp
from routes.ambulantes import ambulantes_bp
from routes.produtos import produtos_bp
from routes.categorias import categorias_bp
from routes.regras_cobranca import regras_cobranca_bp
from routes.usuarios import usuarios_bp
from routes.pedidos import pedidos_bp
from routes.relatorios import relatorios_bp
from routes.logs import logs_bp

def create_app(config_name=None):
    """
    Factory function para criar a aplicação Flask
    """
    app = Flask(__name__)
    
    # Determina o ambiente
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Carrega configurações
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Inicializa extensões
    init_db(app)
    
    # Configura CORS
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Configura JWT
    jwt = JWTManager(app)
    
    # Handlers para JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token expirado'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'message': 'Token inválido'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'message': 'Token de autorização requerido'}), 401
    
    # Registra blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(ambulantes_bp, url_prefix='/api/ambulantes')
    app.register_blueprint(produtos_bp, url_prefix='/api/produtos')
    app.register_blueprint(categorias_bp, url_prefix='/api/categorias')
    app.register_blueprint(regras_cobranca_bp, url_prefix='/api/regras-cobranca')
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
    app.register_blueprint(pedidos_bp, url_prefix='/api/pedidos')
    app.register_blueprint(relatorios_bp, url_prefix='/api/relatorios')
    app.register_blueprint(logs_bp, url_prefix='/api/logs')
    
    # Rota de status da API
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
    
    # Handler para erros 404
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Endpoint não encontrado'}), 404
    
    # Handler para erros 500
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500
    
    # Handler para erros de validação
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'message': 'Requisição inválida'}), 400
    
    # Middleware para adicionar cabeçalhos de segurança
    @app.after_request
    def after_request(response):
        # Cabeçalhos de segurança
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # CORS headers (já configurado pelo Flask-CORS, mas garantindo)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        
        return response
    
    # Comando CLI para inicializar o banco de dados
    @app.cli.command()
    def init_db_command():
        """Inicializa o banco de dados"""
        from database import create_tables
        from werkzeug.security import generate_password_hash
        
        create_tables()
        
        # Cria usuário admin padrão se não existir
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@licimar.com',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
        
        # Cria categorias padrão
        categorias_padrao = [
            {'nome': 'Picolés', 'descricao': 'Picolés diversos'},
            {'nome': 'Sorvetes Premium', 'descricao': 'Sorvetes premium e especiais'},
            {'nome': 'Picolés de Fruta', 'descricao': 'Picolés de frutas naturais'},
            {'nome': 'Cones', 'descricao': 'Sorvetes em cone'},
            {'nome': 'Chocolates', 'descricao': 'Chocolates e bombons'},
            {'nome': 'Doces', 'descricao': 'Balas e doces diversos'},
            {'nome': 'Outros', 'descricao': 'Outros produtos'}
        ]
        
        for cat_data in categorias_padrao:
            if not Categoria.query.filter_by(nome=cat_data['nome']).first():
                categoria = Categoria(**cat_data)
                db.session.add(categoria)
        
        # Cria alguns ambulantes padrão
        ambulantes_padrao = [
            {'nome': 'Ivan Magé', 'email': 'ivan@licimar.com', 'telefone': '11987654321'},
            {'nome': 'Roberto Peixoto', 'email': 'roberto@licimar.com', 'telefone': '11912345678'},
            {'nome': 'Sabino', 'email': 'sabino@licimar.com', 'telefone': '11998765432'}
        ]
        
        for amb_data in ambulantes_padrao:
            if not Ambulante.query.filter_by(nome=amb_data['nome']).first():
                ambulante = Ambulante(**amb_data)
                db.session.add(ambulante)
        
        # Cria regra de cobrança padrão
        if not RegraCobranca.query.first():
            regras_padrao = [
                {'faixa_inicial': 0, 'faixa_final': 100, 'percentual': 20, 'descricao': 'Até R$ 100 - 20% de desconto'},
                {'faixa_inicial': 101, 'faixa_final': 300, 'percentual': 15, 'descricao': 'R$ 101 a R$ 300 - 15% de desconto'},
                {'faixa_inicial': 301, 'faixa_final': 999999, 'percentual': 10, 'descricao': 'Acima de R$ 300 - 10% de desconto'}
            ]
            
            for regra_data in regras_padrao:
                regra = RegraCobranca(**regra_data)
                db.session.add(regra)
        
        db.session.commit()
        print('Banco de dados inicializado com sucesso!')
    
    return app

# Ponto de entrada para execução direta
if __name__ == '__main__':
    app = create_app()
    
    # Cria as tabelas se não existirem
    with app.app_context():
        db.create_all()
    
    # Executa o servidor
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
