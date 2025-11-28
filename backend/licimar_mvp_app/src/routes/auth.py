"""
Rotas de autenticação
"""

from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity
)
from werkzeug.security import check_password_hash
from ..models import User
from ..database import db
from ..utils.helpers import register_log, sanitize_string
from ..utils.decorators import token_required  # Certifique-se que esse decorator está correto

auth_bp = Blueprint('auth', __name__)


# ====================== LOGIN ======================
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

        # Busca por username OU email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user or not user.check_password(password):
            register_log(None, 'LOGIN_FAILED', f'Tentativa falhada: {username}')
            return jsonify({'message': 'Credenciais inválidas'}), 401

        if not user.active:
            return jsonify({'message': 'Usuário inativo'}), 401

        # Gerar tokens JWT
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        register_log(user.id, 'LOGIN_SUCCESS', 'Usuário logou com sucesso')

        return jsonify({
            'message': 'Login realizado com sucesso',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        current_app.logger.error(f"Erro no login: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500



# ====================== REFRESH TOKEN ======================
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)  # Requer o refresh token
def refresh():
    """
    Gera novo token de acesso
    """
    try:
        current_user_id = get_jwt_identity()
        current_user_id = int(current_user_id)

        user = User.query.get(current_user_id)

        if not user or not user.active:
            return jsonify({'message': 'Usuário inválido ou inativo'}), 401

        new_access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'access_token': new_access_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        current_app.logger.error(f"Erro ao renovar token: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500



# ====================== PERFIL DO USUÁRIO ======================
@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """
    Retorna o perfil do usuário logado
    """
    try:
        return jsonify({
            'user': g.current_user.to_dict()
        }), 200

    except Exception as e:
        current_app.logger.error(f"Erro ao obter perfil: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500



# ====================== ALTERAR SENHA ======================
@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """
    Permite o usuário alterar a própria senha
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400

        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not all([current_password, new_password, confirm_password]):
            return jsonify({'message': 'Todos os campos são obrigatórios'}), 400

        if new_password != confirm_password:
            return jsonify({'message': 'Nova senha e confirmação não coincidem'}), 400

        if len(new_password) < 6:
            return jsonify({'message': 'Nova senha deve ter pelo menos 6 caracteres'}), 400

        user = g.current_user

        if not user.check_password(current_password):
            return jsonify({'message': 'Senha atual incorreta'}), 400

        user.set_password(new_password)
        db.session.commit()

        register_log(user.id, 'PASSWORD_CHANGED', 'Usuário alterou a senha')

        return jsonify({'message': 'Senha alterada com sucesso'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao alterar senha: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500



# ====================== LOGOUT ======================
@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    Apenas registra o logout
    """
    try:
        register_log(g.current_user.id, 'LOGOUT', 'Logout realizado com sucesso')
        return jsonify({'message': 'Logout realizado com sucesso'}), 200

    except Exception as e:
        current_app.logger.error(f"Erro no logout: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500
