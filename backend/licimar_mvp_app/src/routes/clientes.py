"""
Rotas para gerenciamento de clientes
"""
from flask import Blueprint, request, jsonify, current_app
from ..models import Cliente
from ..database import db
from ..utils.decorators import admin_required, log_action, token_required
from ..utils.helpers import validate_email, validate_cpf, validate_phone, sanitize_string, paginate_query

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('', methods=['GET'])
@token_required
def get_clientes():
    """
    Lista todos os clientes com paginação e filtros
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        status = request.args.get('status', '').strip()
        
        # Constrói a query base
        query = Cliente.query
        
        # Aplica filtros
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Cliente.nome.ilike(search_term)) |
                (Cliente.email.ilike(search_term)) |
                (Cliente.telefone.ilike(search_term))
            )
        
        if status:
            query = query.filter(Cliente.status == status)
        
        # Ordena por nome
        query = query.order_by(Cliente.nome)
        
        # Aplica paginação
        result = paginate_query(query, page, per_page)
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar clientes: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@clientes_bp.route('/<int:cliente_id>', methods=['GET'])
@admin_required
def get_cliente(cliente_id):
    """
    Obtém um cliente específico
    """
    try:
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return jsonify({'message': 'Cliente não encontrado'}), 404
        
        return jsonify(cliente.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter cliente: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@clientes_bp.route('', methods=['POST'])
@admin_required
@log_action('CREATE_CLIENTE')
def create_cliente():
    """
    Cria um novo cliente
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
            existing_cliente = Cliente.query.filter_by(email=email).first()
            if existing_cliente:
                return jsonify({'message': 'Email já cadastrado'}), 409
        
        # Verifica se CPF já existe (se fornecido)
        if cpf:
            existing_cliente = Cliente.query.filter_by(cpf=cpf).first()
            if existing_cliente:
                return jsonify({'message': 'CPF já cadastrado'}), 409
        
        # Cria o cliente
        cliente = Cliente(
            nome=nome,
            email=email,
            telefone=telefone,
            cpf=cpf,
            endereco=endereco,
            status=status
        )
        
        db.session.add(cliente)
        db.session.commit()
        
        return jsonify({
            'message': 'Cliente criado com sucesso',
            'cliente': cliente.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar cliente: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@clientes_bp.route('/<int:cliente_id>', methods=['PUT'])
@admin_required
@log_action('UPDATE_CLIENTE')
def update_cliente(cliente_id):
    """
    Atualiza um cliente existente
    """
    try:
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return jsonify({'message': 'Cliente não encontrado'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Atualiza os campos fornecidos
        if 'nome' in data:
            nome = sanitize_string(data['nome'].strip())
            if not nome:
                return jsonify({'message': 'Nome é obrigatório'}), 400
            cliente.nome = nome
        
        if 'email' in data:
            email = sanitize_string(data['email'].strip()) if data['email'] else None
            if email and not validate_email(email):
                return jsonify({'message': 'Email inválido'}), 400
            
            # Verifica se email já existe em outro cliente
            if email:
                existing_cliente = Cliente.query.filter(
                    Cliente.email == email,
                    Cliente.id != cliente_id
                ).first()
                if existing_cliente:
                    return jsonify({'message': 'Email já cadastrado'}), 409
            
            cliente.email = email
        
        if 'telefone' in data:
            telefone = sanitize_string(data['telefone'].strip()) if data['telefone'] else None
            if telefone and not validate_phone(telefone):
                return jsonify({'message': 'Telefone inválido'}), 400
            cliente.telefone = telefone
        
        if 'cpf' in data:
            cpf = sanitize_string(data['cpf'].strip()) if data['cpf'] else None
            if cpf and not validate_cpf(cpf):
                return jsonify({'message': 'CPF inválido'}), 400
            
            # Verifica se CPF já existe em outro cliente
            if cpf:
                existing_cliente = Cliente.query.filter(
                    Cliente.cpf == cpf,
                    Cliente.id != cliente_id
                ).first()
                if existing_cliente:
                    return jsonify({'message': 'CPF já cadastrado'}), 409
            
            cliente.cpf = cpf
        
        if 'endereco' in data:
            cliente.endereco = sanitize_string(data['endereco'].strip()) if data['endereco'] else None
        
        if 'status' in data:
            status = data['status']
            if status not in ['ativo', 'inativo']:
                return jsonify({'message': 'Status deve ser "ativo" ou "inativo"'}), 400
            cliente.status = status
        
        if 'divida_acumulada' in data:
            try:
                divida = float(data['divida_acumulada'])
                if divida < 0:
                    return jsonify({'message': 'Dívida acumulada não pode ser negativa'}), 400
                cliente.divida_acumulada = divida
            except (ValueError, TypeError):
                return jsonify({'message': 'Dívida acumulada deve ser um número válido'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cliente atualizado com sucesso',
            'cliente': cliente.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar cliente: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@clientes_bp.route('/<int:cliente_id>', methods=['DELETE'])
@admin_required
@log_action('DELETE_CLIENTE')
def delete_cliente(cliente_id):
    """
    Remove um cliente
    """
    try:
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return jsonify({'message': 'Cliente não encontrado'}), 404
        
        # Verifica se o cliente tem pedidos associados
        if cliente.pedidos:
            return jsonify({
                'message': 'Não é possível excluir cliente com pedidos associados. '
                          'Altere o status para "inativo" se necessário.'
            }), 409
        
        db.session.delete(cliente)
        db.session.commit()
        
        return jsonify({'message': 'Cliente removido com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao remover cliente: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@clientes_bp.route('/ativos', methods=['GET'])
@token_required
def get_clientes_ativos():
    """
    Lista apenas clientes ativos (para seleção em formulários)
    """
    try:
        clientes = Cliente.query.filter_by(status='ativo').order_by(Cliente.nome).all()
        
        return jsonify([cliente.to_dict() for cliente in clientes]), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar clientes ativos: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500
