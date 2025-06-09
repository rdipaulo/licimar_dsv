from flask import Blueprint, request, jsonify, g, current_app
from src.database import db
from src.models import vendedor
from src.utils.decorators import token_required, role_required
from src.utils.helpers import register_log

vendedores_bp = Blueprint("vendedores", __name__)

# Rota para listar todos os vendedores (protegida por token)
@vendedores_bp.route("", methods=["GET"])
@token_required
def get_vendedores():
    try:
        vendedores = vendedor.query.filter_by(active=True).all()
        output = [
            {
                "id": vendedor.id,
                "nome": vendedor.nome,
                "email": vendedor.email,
                "telefone": vendedor.telefone,
                "active": vendedor.active
            } for vendedor in vendedores
        ]
        return jsonify(output), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar vendedores: {e}")
        return jsonify({"message": "Erro ao buscar vendedores."}), 500

# Rota para buscar um vendedor específico pelo ID (protegida por token)
@vendedores_bp.route("/<int:vendedor_id>", methods=["GET"])
@token_required
def get_vendedor(vendedor_id):
    vendedor = vendedor.query.get_or_404(vendedor_id)
    if not vendedor.active:
        return jsonify({"message": "Vendedor não encontrado ou inativo."}), 404
        
    return jsonify({
        "id": vendedor.id,
        "nome": vendedor.nome,
        "email": vendedor.email,
        "telefone": vendedor.telefone,
        "active": vendedor.active
    }), 200

# Rota para criar um novo vendedor (requer papel admin ou manager)
@vendedores_bp.route("", methods=["POST"])
@role_required(["admin", "manager"])
def create_vendedor():
    data = request.get_json()
    if not data or not data.get("nome"):
        return jsonify({"message": "Nome do vendedor é obrigatório!"}), 400

    # Verifica se já existe um vendedor com o mesmo nome
    if vendedor.query.filter_by(nome=data["nome"]).first():
        return jsonify({"message": "Já existe um vendedor com este nome!"}), 409

    novo_vendedor = vendedor(
        nome=data["nome"],
        email=data.get("email"),
        telefone=data.get("telefone"),
        active=data.get("active", True)
    )
    
    try:
        db.session.add(novo_vendedor)
        db.session.commit()
        register_log("CREATE", "Vendedor", novo_vendedor.id, f"Vendedor criado: {novo_vendedor.nome}")
        return jsonify({
            "message": "Vendedor criado com sucesso!", 
            "vendedor": {"id": novo_vendedor.id, "nome": novo_vendedor.nome}
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao criar vendedor: {e}")
        return jsonify({"message": "Erro interno ao criar vendedor."}), 500

# Rota para atualizar um vendedor (requer papel admin ou manager)
@vendedores_bp.route("/<int:vendedor_id>", methods=["PUT"])
@role_required(["admin", "manager"])
def update_vendedor(vendedor_id):
    vendedor = vendedor.query.get_or_404(vendedor_id)
    data = request.get_json()
    if not data:
        return jsonify({"message": "Nenhum dado fornecido para atualização."}), 400

    # Verifica se o novo nome já existe (se estiver sendo alterado)
    if "nome" in data and data["nome"] != vendedor.nome and vendedor.query.filter_by(nome=data["nome"]).first():
        return jsonify({"message": "Já existe um vendedor com este nome!"}), 409

    # Guarda os dados antigos para log
    old_data = {field: getattr(vendedor, field) for field in data.keys() if hasattr(vendedor, field)}

    # Atualiza os campos fornecidos
    vendedor.nome = data.get("nome", vendedor.nome)
    vendedor.email = data.get("email", vendedor.email)
    vendedor.telefone = data.get("telefone", vendedor.telefone)
    vendedor.active = data.get("active", vendedor.active)
    
    try:
        db.session.commit()
        register_log("UPDATE", "Vendedor", vendedor.id, {"old": old_data, "new": data})
        return jsonify({"message": "Vendedor atualizado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao atualizar vendedor {vendedor_id}: {e}")
        return jsonify({"message": "Erro interno ao atualizar vendedor."}), 500

# Rota para deletar um vendedor (inativar) (requer papel admin)
@vendedores_bp.route("/<int:vendedor_id>", methods=["DELETE"])
@role_required("admin")
def delete_vendedor(vendedor_id):
    vendedor = vendedor.query.get_or_404(vendedor_id)
    
    if not vendedor.active:
        return jsonify({"message": "Vendedor já está inativo."}), 400

    vendedor.active = False # Deleção lógica
    
    try:
        db.session.commit()
        register_log("DELETE", "Vendedor", vendedor.id, f"Vendedor inativado: {vendedor.nome}")
        return jsonify({"message": "Vendedor inativado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao inativar vendedor {vendedor_id}: {e}")
        return jsonify({"message": "Erro interno ao inativar vendedor."}), 500
