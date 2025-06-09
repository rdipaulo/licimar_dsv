from flask import Blueprint, request, jsonify, g, current_app
from src.database import db
from src.models import produto
from src.utils.decorators import token_required, role_required
from src.utils.helpers import register_log

produtos_bp = Blueprint("produtos", __name__)

# Rota para listar todos os produtos (protegida por token)
@produtos_bp.route("", methods=["GET"])
@token_required
def get_produtos():
    try:
        produtos = produto.query.filter_by(active=True).all()
        # Converte a lista de objetos Produto para uma lista de dicionários
        output = [
            {
                "id": produto.id,
                "nome": produto.nome,
                "preco_venda": str(produto.preco_venda), # Converte Decimal para string
                "estoque": produto.estoque,
                "imagem_url": produto.imagem_url,
                "descricao": produto.descricao,
                "categoria": produto.categoria,
                "active": produto.active
            } for produto in produtos
        ]
        return jsonify(output), 200
    except Exception as e:
        # Logar o erro real
        current_app.logger.error(f"Erro ao buscar produtos: {e}")
        return jsonify({"message": "Erro ao buscar produtos."}), 500

# Rota para buscar um produto específico pelo ID (protegida por token)
@produtos_bp.route("/<int:produto_id>", methods=["GET"])
@token_required
def get_produto(produto_id):
    produto = produto.query.get_or_404(produto_id)
    if not produto.active:
         return jsonify({"message": "Produto não encontrado ou inativo."}), 404
         
    return jsonify({
        "id": produto.id,
        "nome": produto.nome,
        "preco_venda": str(produto.preco_venda),
        "estoque": produto.estoque,
        "imagem_url": produto.imagem_url,
        "descricao": produto.descricao,
        "categoria": produto.categoria,
        "active": produto.active
    }), 200

# Rota para criar um novo produto (requer papel admin ou manager)
@produtos_bp.route("", methods=["POST"])
@role_required(["admin", "manager"]) # Somente admin ou manager podem criar
def create_produto():
    data = request.get_json()
    if not data or not data.get("nome") or data.get("preco_venda") is None or data.get("estoque") is None:
        return jsonify({"message": "Nome, preço de venda e estoque são obrigatórios!"}), 400

    novo_produto = produto(
        nome=data["nome"],
        preco_venda=data["preco_venda"],
        estoque=data["estoque"],
        imagem_url=data.get("imagem_url"),
        descricao=data.get("descricao"),
        categoria=data.get("categoria"),
        active=data.get("active", True)
    )
    
    try:
        db.session.add(novo_produto)
        db.session.commit()
        register_log("CREATE", "Produto", novo_produto.id, f"Produto criado: {novo_produto.nome}")
        return jsonify({
            "message": "Produto criado com sucesso!", 
            "produto": {"id": novo_produto.id, "nome": novo_produto.nome}
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao criar produto: {e}")
        return jsonify({"message": "Erro interno ao criar produto."}), 500

# Rota para atualizar um produto (requer papel admin ou manager)
@produtos_bp.route("/<int:produto_id>", methods=["PUT"])
@role_required(["admin", "manager"])
def update_produto(produto_id):
    produto = produto.query.get_or_404(produto_id)
    data = request.get_json()
    if not data:
        return jsonify({"message": "Nenhum dado fornecido para atualização."}), 400

    # Guarda os dados antigos para log (opcional)
    old_data = {field: getattr(produto, field) for field in data.keys() if hasattr(produto, field)}

    # Atualiza os campos fornecidos
    produto.nome = data.get("nome", produto.nome)
    produto.preco_venda = data.get("preco_venda", produto.preco_venda)
    produto.estoque = data.get("estoque", produto.estoque)
    produto.imagem_url = data.get("imagem_url", produto.imagem_url)
    produto.descricao = data.get("descricao", produto.descricao)
    produto.categoria = data.get("categoria", produto.categoria)
    produto.active = data.get("active", produto.active)
    
    try:
        db.session.commit()
        register_log("UPDATE", "Produto", produto.id, {"old": old_data, "new": data})
        return jsonify({"message": "Produto atualizado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao atualizar produto {produto_id}: {e}")
        return jsonify({"message": "Erro interno ao atualizar produto."}), 500

# Rota para deletar um produto (inativar) (requer papel admin)
@produtos_bp.route("/<int:produto_id>", methods=["DELETE"])
@role_required("admin") # Somente admin pode "deletar" (inativar)
def delete_produto(produto_id):
    produto = produto.query.get_or_404(produto_id)
    
    if not produto.active:
         return jsonify({"message": "Produto já está inativo."}), 400

    produto.active = False # Deleção lógica, apenas inativa
    
    try:
        db.session.commit()
        register_log("DELETE", "Produto", produto.id, f"Produto inativado: {produto.nome}")
        return jsonify({"message": "Produto inativado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao inativar produto {produto_id}: {e}")
        return jsonify({"message": "Erro interno ao inativar produto."}), 500
