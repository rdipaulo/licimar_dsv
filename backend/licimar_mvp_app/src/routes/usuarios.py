"""
Rotas para gerenciamento de usuários do sistema
"""
from flask import Blueprint, request, jsonify, current_app
from ..models import User
from ..database import db
from ..utils.decorators import admin_required, log_action
from ..utils.helpers import validate_email, sanitize_string, paginate_query, register_log

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('', methods=['GET'])
@admin_required
def get_usuarios():
    """
    Lista todos os usuários com paginação e filtros
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        role = request.args.get('role', '').strip()
        active_only = request.args.get('active_only', type=bool)
        
        # Constrói a query base
        query = User.query
        
        # Aplica filtros
        if active_only is not None:
            query = query.filter(User.active == active_only)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.username.ilike(search_term)) |
                (User.email.ilike(search_term))
            )
        
        if role:
            query = query.filter(User.role == role)
        
        # Ordena por username
        query = query.order_by(User.username)
        
        # Aplica paginação
        result = paginate_query(query, page, per_page)
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar usuários: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@usuarios_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_usuario(user_id):
    """
    Obtém um usuário específico
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter usuário: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@usuarios_bp.route('', methods=['POST'])
@admin_required
@log_action('CREATE_USER')
def create_usuario():
    """
    Cria um novo usuário
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Validação dos campos obrigatórios
        username = sanitize_string(data.get('username', '').strip())
        if not username:
            return jsonify({'message': 'Username é obrigatório'}), 400
        
        if len(username) < 3:
            return jsonify({'message': 'Username deve ter pelo menos 3 caracteres'}), 400
        
        email = sanitize_string(data.get('email', '').strip())
        if not email:
            return jsonify({'message': 'Email é obrigatório'}), 400
        
        if not validate_email(email):
            return jsonify({'message': 'Email inválido'}), 400
        
        password = data.get('password', '')
        if not password:
            return jsonify({'message': 'Senha é obrigatória'}), 400
        
        if len(password) < 6:
            return jsonify({'message': 'Senha deve ter pelo menos 6 caracteres'}), 400
        
        role = data.get('role', 'operador')
        if role not in ['admin', 'operador']:
            return jsonify({'message': 'Role deve ser "admin" ou "operador"'}), 400
        
        # Verifica se username já existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'message': 'Username já existe'}), 409
        
        # Verifica se email já existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': 'Email já cadastrado'}), 409
        
        # Cria o usuário
        user = User(
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Registra a criação
        register_log(user.id, 'USER_CREATED', f'Usuário criado: {username}')
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar usuário: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@usuarios_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
@log_action('UPDATE_USER')
def update_usuario(user_id):
    """
    Atualiza um usuário existente
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Atualiza os campos fornecidos
        if 'username' in data:
            username = sanitize_string(data['username'].strip())
            if not username:
                return jsonify({'message': 'Username é obrigatório'}), 400
            
            if len(username) < 3:
                return jsonify({'message': 'Username deve ter pelo menos 3 caracteres'}), 400
            
            # Verifica se username já existe em outro usuário
            existing_user = User.query.filter(
                User.username == username,
                User.id != user_id
            ).first()
            if existing_user:
                return jsonify({'message': 'Username já existe'}), 409
            
            user.username = username
        
        if 'email' in data:
            email = sanitize_string(data['email'].strip())
            if not email:
                return jsonify({'message': 'Email é obrigatório'}), 400
            
            if not validate_email(email):
                return jsonify({'message': 'Email inválido'}), 400
            
            # Verifica se email já existe em outro usuário
            existing_user = User.query.filter(
                User.email == email,
                User.id != user_id
            ).first()
            if existing_user:
                return jsonify({'message': 'Email já cadastrado'}), 409
            
            user.email = email
        
        if 'role' in data:
            role = data['role']
            if role not in ['admin', 'operador']:
                return jsonify({'message': 'Role deve ser "admin" ou "operador"'}), 400
            user.role = role
        
        if 'active' in data:
            user.active = bool(data['active'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário atualizado com sucesso',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar usuário: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@usuarios_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
@log_action('DELETE_USER')
def delete_usuario(user_id):
    """
    Remove um usuário
    """
    try:
        from flask import g
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Impede que o usuário delete a si mesmo
        if user.id == g.current_user.id:
            return jsonify({'message': 'Não é possível excluir seu próprio usuário'}), 409
        
        # Verifica se é o último admin
        if user.role == 'admin':
            admin_count = User.query.filter_by(role='admin', active=True).count()
            if admin_count <= 1:
                return jsonify({
                    'message': 'Não é possível excluir o último administrador do sistema'
                }), 409
        
        # Verifica se o usuário tem logs associados
        if user.logs:
            # Soft delete - marca como inativo
            user.active = False
            db.session.commit()
            
            return jsonify({
                'message': 'Usuário marcado como inativo devido a logs associados'
            }), 200
        else:
            # Hard delete se não há logs associados
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({'message': 'Usuário removido com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao remover usuário: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@usuarios_bp.route('/<int:user_id>/reset-password', methods=['POST'])
@admin_required
@log_action('RESET_PASSWORD')
def reset_password(user_id):
    """
    Redefine a senha de um usuário
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        new_password = data.get('new_password', '')
        if not new_password:
            return jsonify({'message': 'Nova senha é obrigatória'}), 400
        
        if len(new_password) < 6:
            return jsonify({'message': 'Nova senha deve ter pelo menos 6 caracteres'}), 400
        
        # Redefine a senha
        user.set_password(new_password)
        db.session.commit()
        
        # Registra a redefinição
        register_log(user.id, 'PASSWORD_RESET', f'Senha redefinida por administrador')
        
        return jsonify({'message': 'Senha redefinida com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao redefinir senha: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@usuarios_bp.route('/stats', methods=['GET'])
@admin_required
def get_user_stats():
    """
    Obtém estatísticas dos usuários
    """
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(active=True).count()
        admin_users = User.query.filter_by(role='admin', active=True).count()
        operador_users = User.query.filter_by(role='operador', active=True).count()
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'admin_users': admin_users,
            'operador_users': operador_users
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter estatísticas de usuários: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500
