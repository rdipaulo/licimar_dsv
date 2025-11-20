"""
Rotas para gerenciamento de ambulantes
"""
from flask import Blueprint, request, jsonify, current_app
from ..models import Ambulante
from ..database import db
from ..utils.decorators import admin_required, log_action, token_required
from ..utils.helpers import validate_email, validate_cpf, validate_phone, sanitize_string, paginate_query

ambulantes_bp = Blueprint('ambulantes', __name__)

@ambulantes_bp.route('', methods=['GET'])
@token_required
def get_ambulantes():
    """
    Lista todos os ambulantes com paginação e filtros
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        status = request.args.get('status', '').strip()
        
        # Constrói a query base
        query = Ambulante.query
        
        # Aplica filtros
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Ambulante.nome.ilike(search_term)) |
                (Ambulante.email.ilike(search_term)) |
                (Ambulante.telefone.ilike(search_term))
            )
        
        if status:
            query = query.filter(Ambulante.status == status)
        
        # Ordena por nome
        query = query.order_by(Ambulante.nome)
        
        # Aplica paginação
        result = paginate_query(query, page, per_page)
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar ambulantes: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@ambulantes_bp.route('/<int:ambulante_id>', methods=['GET'])
@admin_required
def get_ambulante(ambulante_id):
    """
    Obtém um ambulante específico
    """
    try:
        ambulante = Ambulante.query.get(ambulante_id)
        
        if not ambulante:
            return jsonify({'message': 'Ambulante não encontrado'}), 404
        
        return jsonify(ambulante.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter ambulante: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@ambulantes_bp.route('', methods=['POST'])
@admin_required
@log_action('CREATE_AMBULANTE')
def create_ambulante():
    """
    Cria um novo ambulante
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Validação dos campos obrigatórios
        nome = sanitize_string(data.get('nome', '').strip())
        if not nome:
            return jsonify({'message': 'Nome é obrigatório'}), 400
        
        # Validação dos campos opcionais
        email = sanitize_string(data.get('email', '').strip()) if data.get('email') else None
        telefone = sanitize_string(data.get('telefone', '').strip()) if data.get('telefone') else None
        cpf = sanitize_string(data.get('cpf', '').strip()) if data.get('cpf') else None
        endereco = sanitize_string(data.get('endereco', '').strip()) if data.get('endereco') else None
        status = data.get('status', 'ativo')
        
        # Validações específicas
        if email and not validate_email(email):
            return jsonify({'message': 'Email inválido'}), 400
        
        if telefone and not validate_phone(telefone):
            return jsonify({'message': 'Telefone inválido'}), 400
        
        if cpf and not validate_cpf(cpf):
            return jsonify({'message': 'CPF inválido'}), 400
        
        if status not in ['ativo', 'inativo']:
            return jsonify({'message': 'Status deve ser "ativo" ou "inativo"'}), 400
        
        # Verifica se email já existe (se fornecido)
        if email:
            existing_ambulante = Ambulante.query.filter_by(email=email).first()
            if existing_ambulante:
                return jsonify({'message': 'Email já cadastrado'}), 409
        
        # Verifica se CPF já existe (se fornecido)
        if cpf:
            existing_ambulante = Ambulante.query.filter_by(cpf=cpf).first()
            if existing_ambulante:
                return jsonify({'message': 'CPF já cadastrado'}), 409
        
        # Cria o ambulante
        ambulante = Ambulante(
            nome=nome,
            email=email,
            telefone=telefone,
            cpf=cpf,
            endereco=endereco,
            status=status
        )
        
        db.session.add(ambulante)
        db.session.commit()
        
        return jsonify({
            'message': 'Ambulante criado com sucesso',
            'ambulante': ambulante.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar ambulante: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@ambulantes_bp.route('/<int:ambulante_id>', methods=['PUT'])
@admin_required
@log_action('UPDATE_AMBULANTE')
def update_ambulante(ambulante_id):
    """
    Atualiza um ambulante existente
    """
    try:
        ambulante = Ambulante.query.get(ambulante_id)
        
        if not ambulante:
            return jsonify({'message': 'Ambulante não encontrado'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Atualiza os campos fornecidos
        if 'nome' in data:
            nome = sanitize_string(data['nome'].strip())
            if not nome:
                return jsonify({'message': 'Nome é obrigatório'}), 400
            ambulante.nome = nome
        
        if 'email' in data:
            email = sanitize_string(data['email'].strip()) if data['email'] else None
            if email and not validate_email(email):
                return jsonify({'message': 'Email inválido'}), 400
            
            # Verifica se email já existe em outro ambulante
            if email:
                existing_ambulante = Ambulante.query.filter(
                    Ambulante.email == email,
                    Ambulante.id != ambulante_id
                ).first()
                if existing_ambulante:
                    return jsonify({'message': 'Email já cadastrado'}), 409
            
            ambulante.email = email
        
        if 'telefone' in data:
            telefone = sanitize_string(data['telefone'].strip()) if data['telefone'] else None
            if telefone and not validate_phone(telefone):
                return jsonify({'message': 'Telefone inválido'}), 400
            ambulante.telefone = telefone
        
        if 'cpf' in data:
            cpf = sanitize_string(data['cpf'].strip()) if data['cpf'] else None
            if cpf and not validate_cpf(cpf):
                return jsonify({'message': 'CPF inválido'}), 400
            
            # Verifica se CPF já existe em outro ambulante
            if cpf:
                existing_ambulante = Ambulante.query.filter(
                    Ambulante.cpf == cpf,
                    Ambulante.id != ambulante_id
                ).first()
                if existing_ambulante:
                    return jsonify({'message': 'CPF já cadastrado'}), 409
            
            ambulante.cpf = cpf
        
        if 'endereco' in data:
            ambulante.endereco = sanitize_string(data['endereco'].strip()) if data['endereco'] else None
        
        if 'status' in data:
            status = data['status']
            if status not in ['ativo', 'inativo']:
                return jsonify({'message': 'Status deve ser "ativo" ou "inativo"'}), 400
            ambulante.status = status
        
        db.session.commit()
        
        return jsonify({
            'message': 'Ambulante atualizado com sucesso',
            'ambulante': ambulante.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar ambulante: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@ambulantes_bp.route('/<int:ambulante_id>', methods=['DELETE'])
@admin_required
@log_action('DELETE_AMBULANTE')
def delete_ambulante(ambulante_id):
    """
    Remove um ambulante
    """
    try:
        ambulante = Ambulante.query.get(ambulante_id)
        
        if not ambulante:
            return jsonify({'message': 'Ambulante não encontrado'}), 404
        
        # Verifica se o ambulante tem pedidos associados
        if ambulante.pedidos:
            return jsonify({
                'message': 'Não é possível excluir ambulante com pedidos associados. '
                          'Altere o status para "inativo" se necessário.'
            }), 409
        
        db.session.delete(ambulante)
        db.session.commit()
        
        return jsonify({'message': 'Ambulante removido com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao remover ambulante: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@ambulantes_bp.route('/ativos', methods=['GET'])
@admin_required
def get_ambulantes_ativos():
    """
    Lista apenas ambulantes ativos (para seleção em formulários)
    """
    try:
        ambulantes = Ambulante.query.filter_by(status='ativo').order_by(Ambulante.nome).all()
        
        return jsonify([ambulante.to_dict() for ambulante in ambulantes]), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar ambulantes ativos: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500
