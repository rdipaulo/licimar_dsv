"""
Decoradores para autenticação e autorização
"""
from functools import wraps
from flask import jsonify, request, current_app, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from models import User, Log
from database import db

def token_required(f):
    """
    Decorador que exige autenticação via JWT
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user or not current_user.active:
                return jsonify({'message': 'Token inválido ou usuário inativo'}), 401
            
            # Adiciona o usuário atual ao contexto global
            g.current_user = current_user
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Token inválido', 'error': str(e)}), 401
    
    return decorated_function

def role_required(required_role):
    """
    Decorador que exige um papel específico do usuário
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                current_user = User.query.get(current_user_id)
                
                if not current_user or not current_user.active:
                    return jsonify({'message': 'Token inválido ou usuário inativo'}), 401
                
                if current_user.role != required_role and current_user.role != 'admin':
                    return jsonify({'message': 'Acesso negado. Privilégios insuficientes'}), 403
                
                # Adiciona o usuário atual ao contexto global
                g.current_user = current_user
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'message': 'Erro de autorização', 'error': str(e)}), 401
        
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorador que exige privilégios de administrador
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user or not current_user.active:
                return jsonify({'message': 'Token inválido ou usuário inativo'}), 401
            
            if not current_user.is_admin():
                return jsonify({'message': 'Acesso negado. Privilégios de administrador necessários'}), 403
            
            # Adiciona o usuário atual ao contexto global
            g.current_user = current_user
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Erro de autorização', 'error': str(e)}), 401
    
    return decorated_function

def log_action(action):
    """
    Decorador para registrar ações do usuário
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Executa a função original
            result = f(*args, **kwargs)
            
            # Registra a ação no log
            try:
                if hasattr(g, 'current_user') and g.current_user:
                    log_entry = Log(
                        user_id=g.current_user.id,
                        action=action,
                        details=f"Endpoint: {request.endpoint}, Method: {request.method}",
                        ip_address=request.remote_addr,
                        user_agent=request.user_agent.string
                    )
                    db.session.add(log_entry)
                    db.session.commit()
            except Exception as e:
                current_app.logger.error(f"Erro ao registrar log: {e}")
            
            return result
        
        return decorated_function
    return decorator
