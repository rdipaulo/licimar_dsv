"""
Rotas para gerenciamento de produtos
"""
from flask import Blueprint, request, jsonify, current_app
from ..models import Produto, Categoria
from ..database import db
from ..utils.decorators import admin_required, token_required, log_action
from ..utils.helpers import sanitize_string, paginate_query

produtos_bp = Blueprint('produtos', __name__)

@produtos_bp.route('', methods=['GET'])
@token_required
def get_produtos():
    """
    Lista todos os produtos com paginação e filtros
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        categoria_id = request.args.get('categoria_id', type=int)
        estoque_baixo = request.args.get('estoque_baixo', type=bool)
        active_only = request.args.get('active_only', True, type=bool)
        
        # Constrói a query base
        query = Produto.query
        
        # Aplica filtros
        if active_only:
            query = query.filter(Produto.active == True)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(Produto.nome.ilike(search_term))
        
        if categoria_id:
            query = query.filter(Produto.categoria_id == categoria_id)
        
        if estoque_baixo:
            query = query.filter(Produto.estoque <= Produto.estoque_minimo)
        
        # Ordena por nome
        query = query.order_by(Produto.nome)
        
        # Aplica paginação
        result = paginate_query(query, page, per_page)
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar produtos: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@produtos_bp.route('/<int:produto_id>', methods=['GET'])
@token_required
def get_produto(produto_id):
    """
    Obtém um produto específico
    """
    try:
        produto = Produto.query.get(produto_id)
        
        if not produto:
            return jsonify({'message': 'Produto não encontrado'}), 404
        
        return jsonify(produto.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter produto: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@produtos_bp.route('', methods=['POST'])
@admin_required
@log_action('CREATE_PRODUTO')
def create_produto():
    """
    Cria um novo produto
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Validação dos campos obrigatórios
        nome = sanitize_string(data.get('nome', '').strip())
        if not nome:
            return jsonify({'message': 'Nome é obrigatório'}), 400
        
        try:
            preco = float(data.get('preco', 0))
            if preco <= 0:
                return jsonify({'message': 'Preço deve ser maior que zero'}), 400
        except (ValueError, TypeError):
            return jsonify({'message': 'Preço inválido'}), 400
        
        try:
            estoque = int(data.get('estoque', 0))
            if estoque < 0:
                return jsonify({'message': 'Estoque não pode ser negativo'}), 400
        except (ValueError, TypeError):
            return jsonify({'message': 'Estoque inválido'}), 400
        
        # Validação dos campos opcionais
        categoria_id = data.get('categoria_id', type=int)
        if categoria_id:
            categoria = Categoria.query.get(categoria_id)
            if not categoria or not categoria.active:
                return jsonify({'message': 'Categoria inválida ou inativa'}), 400
        
        descricao = sanitize_string(data.get('descricao', '').strip()) if data.get('descricao') else None
        imagem_url = sanitize_string(data.get('imagem_url', '').strip()) if data.get('imagem_url') else None
        
        try:
            estoque_minimo = int(data.get('estoque_minimo', 10))
            if estoque_minimo < 0:
                return jsonify({'message': 'Estoque mínimo não pode ser negativo'}), 400
        except (ValueError, TypeError):
            estoque_minimo = 10
        
        # Verifica se produto já existe
        existing_produto = Produto.query.filter_by(nome=nome).first()
        if existing_produto:
            return jsonify({'message': 'Produto com este nome já existe'}), 409
        
        # Cria o produto
        produto = Produto(
            nome=nome,
            preco=preco,
            estoque=estoque,
            categoria_id=categoria_id,
            descricao=descricao,
            imagem_url=imagem_url,
            estoque_minimo=estoque_minimo
        )
        
        db.session.add(produto)
        db.session.commit()
        
        return jsonify({
            'message': 'Produto criado com sucesso',
            'produto': produto.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar produto: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@produtos_bp.route('/<int:produto_id>', methods=['PUT'])
@admin_required
@log_action('UPDATE_PRODUTO')
def update_produto(produto_id):
    """
    Atualiza um produto existente
    """
    try:
        produto = Produto.query.get(produto_id)
        
        if not produto:
            return jsonify({'message': 'Produto não encontrado'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Atualiza os campos fornecidos
        if 'nome' in data:
            nome = sanitize_string(data['nome'].strip())
            if not nome:
                return jsonify({'message': 'Nome é obrigatório'}), 400
            
            # Verifica se nome já existe em outro produto
            existing_produto = Produto.query.filter(
                Produto.nome == nome,
                Produto.id != produto_id
            ).first()
            if existing_produto:
                return jsonify({'message': 'Produto com este nome já existe'}), 409
            
            produto.nome = nome
        
        if 'preco' in data:
            try:
                preco = float(data['preco'])
                if preco <= 0:
                    return jsonify({'message': 'Preço deve ser maior que zero'}), 400
                produto.preco = preco
            except (ValueError, TypeError):
                return jsonify({'message': 'Preço inválido'}), 400
        
        if 'estoque' in data:
            try:
                estoque = int(data['estoque'])
                if estoque < 0:
                    return jsonify({'message': 'Estoque não pode ser negativo'}), 400
                produto.estoque = estoque
            except (ValueError, TypeError):
                return jsonify({'message': 'Estoque inválido'}), 400
        
        if 'categoria_id' in data:
            categoria_id = data['categoria_id']
            if categoria_id:
                categoria = Categoria.query.get(categoria_id)
                if not categoria or not categoria.active:
                    return jsonify({'message': 'Categoria inválida ou inativa'}), 400
            produto.categoria_id = categoria_id
        
        if 'descricao' in data:
            produto.descricao = sanitize_string(data['descricao'].strip()) if data['descricao'] else None
        
        if 'imagem_url' in data:
            produto.imagem_url = sanitize_string(data['imagem_url'].strip()) if data['imagem_url'] else None
        
        if 'estoque_minimo' in data:
            try:
                estoque_minimo = int(data['estoque_minimo'])
                if estoque_minimo < 0:
                    return jsonify({'message': 'Estoque mínimo não pode ser negativo'}), 400
                produto.estoque_minimo = estoque_minimo
            except (ValueError, TypeError):
                return jsonify({'message': 'Estoque mínimo inválido'}), 400
        
        if 'active' in data:
            produto.active = bool(data['active'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Produto atualizado com sucesso',
            'produto': produto.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar produto: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@produtos_bp.route('/<int:produto_id>', methods=['DELETE'])
@admin_required
@log_action('DELETE_PRODUTO')
def delete_produto(produto_id):
    """
    Remove um produto (soft delete - marca como inativo)
    """
    try:
        produto = Produto.query.get(produto_id)
        
        if not produto:
            return jsonify({'message': 'Produto não encontrado'}), 404
        
        # Verifica se o produto tem itens de pedido associados
        if produto.itens_pedido:
            # Soft delete - marca como inativo
            produto.active = False
            db.session.commit()
            
            return jsonify({
                'message': 'Produto marcado como inativo devido a pedidos associados'
            }), 200
        else:
            # Hard delete se não há pedidos associados
            db.session.delete(produto)
            db.session.commit()
            
            return jsonify({'message': 'Produto removido com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao remover produto: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@produtos_bp.route('/estoque-baixo', methods=['GET'])
@admin_required
def get_produtos_estoque_baixo():
    """
    Lista produtos com estoque baixo
    """
    try:
        produtos = Produto.query.filter(
            Produto.estoque <= Produto.estoque_minimo,
            Produto.active == True
        ).order_by(Produto.nome).all()
        
        return jsonify([produto.to_dict() for produto in produtos]), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar produtos com estoque baixo: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@produtos_bp.route('/<int:produto_id>/ajustar-estoque', methods=['POST'])
@admin_required
@log_action('ADJUST_ESTOQUE')
def ajustar_estoque(produto_id):
    """
    Ajusta o estoque de um produto
    """
    try:
        produto = Produto.query.get(produto_id)
        
        if not produto:
            return jsonify({'message': 'Produto não encontrado'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        try:
            novo_estoque = int(data.get('novo_estoque', 0))
            if novo_estoque < 0:
                return jsonify({'message': 'Estoque não pode ser negativo'}), 400
        except (ValueError, TypeError):
            return jsonify({'message': 'Estoque inválido'}), 400
        
        estoque_anterior = produto.estoque
        produto.estoque = novo_estoque
        
        db.session.commit()
        
        return jsonify({
            'message': 'Estoque ajustado com sucesso',
            'produto': produto.to_dict(),
            'estoque_anterior': estoque_anterior,
            'novo_estoque': novo_estoque
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao ajustar estoque: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500
