"""
Rotas de autenticação
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from ..models import User
from ..database import db
from ..utils.helpers import register_log, validate_email, sanitize_string
from ..utils.decorators import token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint para login de usuários
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        username = sanitize_string(data.get('username', '').strip())
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'message': 'Username e senha são obrigatórios'}), 400
        
        # Busca usuário por username ou email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            register_log(None, 'LOGIN_FAILED', f'Tentativa de login falhada para: {username}')
            return jsonify({'message': 'Credenciais inválidas'}), 401
        
        if not user.active:
            return jsonify({'message': 'Usuário inativo'}), 401
        
        # Cria tokens JWT (identity deve ser string)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Registra login bem-sucedido
        register_log(user.id, 'LOGIN_SUCCESS', f'Login realizado com sucesso')
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no login: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Endpoint para renovar token de acesso
    """
    try:
        current_user_id = get_jwt_identity()
        # Converter para int se necessário
        current_user_id = int(current_user_id) if isinstance(current_user_id, str) else current_user_id
        user = User.query.get(current_user_id)
        
        if not user or not user.active:
            return jsonify({'message': 'Usuário inválido ou inativo'}), 401
        
        # Cria novo token de acesso
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao renovar token: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """
    Endpoint para obter perfil do usuário atual
    """
    try:
        from flask import g
        return jsonify({
            'user': g.current_user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter perfil: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """
    Endpoint para alterar senha do usuário
    """
    try:
        from flask import g
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not all([current_password, new_password, confirm_password]):
            return jsonify({'message': 'Todos os campos são obrigatórios'}), 400
        
        if new_password != confirm_password:
            return jsonify({'message': 'Nova senha e confirmação não coincidem'}), 400
        
        if len(new_password) < 6:
            return jsonify({'message': 'Nova senha deve ter pelo menos 6 caracteres'}), 400
        
        user = g.current_user
        
        if not user.check_password(current_password):
            return jsonify({'message': 'Senha atual incorreta'}), 400
        
        # Atualiza a senha
        user.set_password(new_password)
        db.session.commit()
        
        # Registra a alteração
        register_log(user.id, 'PASSWORD_CHANGED', 'Senha alterada pelo usuário')
        
        return jsonify({'message': 'Senha alterada com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao alterar senha: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    Endpoint para logout (registra a ação)
    """
    try:
        from flask import g
        register_log(g.current_user.id, 'LOGOUT', 'Logout realizado')
        
        return jsonify({'message': 'Logout realizado com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no logout: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500
