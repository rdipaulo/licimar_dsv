"""
Rotas para gerenciamento de categorias de produtos
"""
from flask import Blueprint, request, jsonify, current_app
from ..models import Categoria, Produto
from ..database import db
from ..utils.decorators import admin_required, token_required, log_action
from ..utils.helpers import sanitize_string, paginate_query

categorias_bp = Blueprint('categorias', __name__)

@categorias_bp.route('', methods=['GET'])
@token_required
def get_categorias():
    """
    Lista todas as categorias com paginação e filtros
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        active_only = request.args.get('active_only', True, type=bool)
        
        # Constrói a query base
        query = Categoria.query
        
        # Aplica filtros
        if active_only:
            query = query.filter(Categoria.active == True)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Categoria.nome.ilike(search_term)) |
                (Categoria.descricao.ilike(search_term))
            )
        
        # Ordena por nome
        query = query.order_by(Categoria.nome)
        
        # Aplica paginação
        result = paginate_query(query, page, per_page)
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar categorias: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@categorias_bp.route('/<int:categoria_id>', methods=['GET'])
@token_required
def get_categoria(categoria_id):
    """
    Obtém uma categoria específica
    """
    try:
        categoria = Categoria.query.get(categoria_id)
        
        if not categoria:
            return jsonify({'message': 'Categoria não encontrada'}), 404
        
        return jsonify(categoria.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter categoria: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@categorias_bp.route('', methods=['POST'])
@admin_required
@log_action('CREATE_CATEGORIA')
def create_categoria():
    """
    Cria uma nova categoria
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
        descricao = sanitize_string(data.get('descricao', '').strip()) if data.get('descricao') else None
        
        # Verifica se categoria já existe
        existing_categoria = Categoria.query.filter_by(nome=nome).first()
        if existing_categoria:
            return jsonify({'message': 'Categoria com este nome já existe'}), 409
        
        # Cria a categoria
        categoria = Categoria(
            nome=nome,
            descricao=descricao
        )
        
        db.session.add(categoria)
        db.session.commit()
        
        return jsonify({
            'message': 'Categoria criada com sucesso',
            'categoria': categoria.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar categoria: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@categorias_bp.route('/<int:categoria_id>', methods=['PUT'])
@admin_required
@log_action('UPDATE_CATEGORIA')
def update_categoria(categoria_id):
    """
    Atualiza uma categoria existente
    """
    try:
        categoria = Categoria.query.get(categoria_id)
        
        if not categoria:
            return jsonify({'message': 'Categoria não encontrada'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Atualiza os campos fornecidos
        if 'nome' in data:
            nome = sanitize_string(data['nome'].strip())
            if not nome:
                return jsonify({'message': 'Nome é obrigatório'}), 400
            
            # Verifica se nome já existe em outra categoria
            existing_categoria = Categoria.query.filter(
                Categoria.nome == nome,
                Categoria.id != categoria_id
            ).first()
            if existing_categoria:
                return jsonify({'message': 'Categoria com este nome já existe'}), 409
            
            categoria.nome = nome
        
        if 'descricao' in data:
            categoria.descricao = sanitize_string(data['descricao'].strip()) if data['descricao'] else None
        
        if 'active' in data:
            categoria.active = bool(data['active'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Categoria atualizada com sucesso',
            'categoria': categoria.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar categoria: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@categorias_bp.route('/<int:categoria_id>', methods=['DELETE'])
@admin_required
@log_action('DELETE_CATEGORIA')
def delete_categoria(categoria_id):
    """
    Remove uma categoria
    """
    try:
        categoria = Categoria.query.get(categoria_id)
        
        if not categoria:
            return jsonify({'message': 'Categoria não encontrada'}), 404
        
        # Verifica se a categoria tem produtos associados
        produtos_count = Produto.query.filter_by(categoria_id=categoria_id).count()
        
        if produtos_count > 0:
            return jsonify({
                'message': f'Não é possível excluir categoria com {produtos_count} produto(s) associado(s). '
                          'Altere o status para "inativo" se necessário.'
            }), 409
        
        db.session.delete(categoria)
        db.session.commit()
        
        return jsonify({'message': 'Categoria removida com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao remover categoria: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@categorias_bp.route('/ativas', methods=['GET'])
@token_required
def get_categorias_ativas():
    """
    Lista apenas categorias ativas (para seleção em formulários)
    """
    try:
        categorias = Categoria.query.filter_by(active=True).order_by(Categoria.nome).all()
        
        return jsonify([categoria.to_dict() for categoria in categorias]), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar categorias ativas: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@categorias_bp.route('/<int:categoria_id>/produtos', methods=['GET'])
@token_required
def get_produtos_categoria(categoria_id):
    """
    Lista produtos de uma categoria específica
    """
    try:
        categoria = Categoria.query.get(categoria_id)
        
        if not categoria:
            return jsonify({'message': 'Categoria não encontrada'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        active_only = request.args.get('active_only', True, type=bool)
        
        # Constrói a query
        query = Produto.query.filter_by(categoria_id=categoria_id)
        
        if active_only:
            query = query.filter(Produto.active == True)
        
        query = query.order_by(Produto.nome)
        
        # Aplica paginação
        result = paginate_query(query, page, per_page)
        
        return jsonify({
            'categoria': categoria.to_dict(),
            'produtos': result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar produtos da categoria: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500
