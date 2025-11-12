"""
Configurações da aplicação Flask
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    """Configuração base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-muito-forte-para-desenvolvimento'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_EXPIRATION_DAYS', 1)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Configurações de CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
    
    # Configurações de upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    # Configurações de paginação
    ITEMS_PER_PAGE = 20
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    
    @staticmethod
    def init_app(app):
        # Define a URI do banco de dados com caminho absoluto
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
            # Usar o instance_path do Flask que já é absoluto
            db_path = os.path.join(app.instance_path, 'licimar_dev.db')
            # Verificar se DATABASE_URL está definido no .env
            db_url = os.environ.get('DATABASE_URL')
            
            # Se DATABASE_URL está no .env mas é relativo ou inválido, ignora
            if db_url and db_url.startswith('sqlite:////home'):
                # Caminho do Docker, substituir pelo caminho local
                app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
            else:
                app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
                
            print(f"[CONFIG] Database path: {db_path}")
            print(f"[CONFIG] Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print(f"[CONFIG] Database exists: {os.path.exists(db_path)}")

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Define a URI do banco de dados com caminho absoluto
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
            db_path = os.path.join(app.instance_path, 'licimar.db')
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or f'sqlite:///{db_path}'
        
        # Log para syslog em produção
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
