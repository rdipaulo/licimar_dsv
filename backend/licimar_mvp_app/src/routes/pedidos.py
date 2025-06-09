from flask import Blueprint, request, jsonify, g, current_app
from src.database import db
from src.models import pedido, item_pedido, produto, vendedor
from src.utils.decorators import token_required, role_required
from src.utils.helpers import register_log
from datetime import datetime

pedidos_bp = Blueprint("pedidos", __name__)

# Rota para listar todos os pedidos (protegida por token)
@pedidos_bp.route("", methods=["GET"])
@token_required
def get_pedidos():
    try:
        pedidos = pedido.query.all()
        output = []
        
        for pedido in pedidos:
            # Busca o vendedor associado ao pedido
            vendedor = vendedor.query.get(pedido.vendedor_id)
            vendedor_nome = vendedor.nome if vendedor else "Desconhecido"
            
            # Formata a data para string legível
            data_operacao = pedido.data_operacao.strftime("%d/%m/%Y %H:%M") if pedido.data_operacao else None
            
            # Adiciona o pedido formatado à lista de saída
            output.append({
                "id": pedido.id,
                "vendedor_id": pedido.vendedor_id,
                "vendedor_nome": vendedor_nome,
                "data_operacao": data_operacao,
                "status": pedido.status,
                "valor_total_a_pagar": str(pedido.valor_total_a_pagar) if pedido.valor_total_a_pagar else None,
                "created_at": pedido.created_at.strftime("%d/%m/%Y %H:%M")
            })
            
        return jsonify(output), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar pedidos: {e}")
        return jsonify({"message": "Erro ao buscar pedidos."}), 500

# Rota para buscar um pedido específico pelo ID com seus itens (protegida por token)
@pedidos_bp.route("/<int:pedido_id>", methods=["GET"])
@token_required
def get_pedido(pedido_id):
    pedido = pedido.query.get_or_404(pedido_id)
    
    try:
        # Busca o vendedor associado ao pedido
        vendedor = vendedor.query.get(pedido.vendedor_id)
        vendedor_nome = vendedor.nome if vendedor else "Desconhecido"
        
        # Formata a data para string legível
        data_operacao = pedido.data_operacao.strftime("%d/%m/%Y %H:%M") if pedido.data_operacao else None
        
        # Busca os itens do pedido
        itens = []
        for item in pedido.itens:
            produto = produto.query.get(item.produto_id)
            produto_nome = produto.nome if produto else "Produto Desconhecido"
            
            itens.append({
                "id": item.id,
                "produto_id": item.produto_id,
                "produto_nome": produto_nome,
                "quantidade_saida": str(item.quantidade_saida),
                "quantidade_retorno": str(item.quantidade_retorno),
                "quantidade_perda": str(item.quantidade_perda),
                "preco_venda_unitario_registrado": str(item.preco_venda_unitario_registrado)
            })
        
        # Monta o objeto de resposta
        pedido_detalhado = {
            "id": pedido.id,
            "vendedor_id": pedido.vendedor_id,
            "vendedor_nome": vendedor_nome,
            "data_operacao": data_operacao,
            "status": pedido.status,
            "valor_total_a_pagar": str(pedido.valor_total_a_pagar) if pedido.valor_total_a_pagar else None,
            "created_at": pedido.created_at.strftime("%d/%m/%Y %H:%M"),
            "itens": itens
        }
            
        return jsonify(pedido_detalhado), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar pedido {pedido_id}: {e}")
        return jsonify({"message": "Erro ao buscar detalhes do pedido."}), 500

# Rota para criar um novo pedido (protegida por token)
@pedidos_bp.route("", methods=["POST"])
@token_required
def create_pedido():
    data = request.get_json()
    if not data or not data.get("vendedor_id") or not data.get("itens"):
        return jsonify({"message": "Vendedor e itens são obrigatórios!"}), 400

    # Verifica se o vendedor existe
    vendedor = vendedor.query.get(data["vendedor_id"])
    if not vendedor:
        return jsonify({"message": "Vendedor não encontrado!"}), 404
    
    # Cria o pedido
    novo_pedido = pedido(
        vendedor_id=data["vendedor_id"],
        data_operacao=datetime.utcnow(),
        status=data.get("status", "EM_ABERTO"),
        created_by=g.user.id # Usa o ID do usuário logado (definido pelo @token_required)
    )
    
    try:
        db.session.add(novo_pedido)
        db.session.flush() # Para obter o ID do pedido antes de adicionar os itens
        
        # Adiciona os itens ao pedido
        for item_data in data["itens"]:
            if not item_data.get("produto_id") or item_data.get("quantidade_saida") is None:
                continue # Pula itens inválidos
                
            # Verifica se o produto existe
            produto = produto.query.get(item_data["produto_id"])
            if not produto:
                continue # Pula produtos que não existem
                
            # Cria o item do pedido
            item = item_pedido(
                pedido_id=novo_pedido.id,
                produto_id=item_data["produto_id"],
                quantidade_saida=item_data["quantidade_saida"],
                quantidade_retorno=item_data.get("quantidade_retorno", 0),
                quantidade_perda=item_data.get("quantidade_perda", 0),
                preco_venda_unitario_registrado=produto.preco_venda # Registra o preço atual
            )
            db.session.add(item)
            
            # Atualiza o estoque do produto (opcional, dependendo da lógica de negócio)
            # produto.estoque -= item_data["quantidade_saida"]
        
        db.session.commit()
        register_log("CREATE", "Pedido", novo_pedido.id, f"Pedido criado para vendedor: {vendedor.nome}")
        return jsonify({
            "message": "Pedido criado com sucesso!", 
            "pedido": {"id": novo_pedido.id, "vendedor": vendedor.nome}
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao criar pedido: {e}")
        return jsonify({"message": "Erro interno ao criar pedido."}), 500

# Rota para atualizar o status de um pedido (protegida por token)
@pedidos_bp.route("/<int:pedido_id>/status", methods=["PUT"])
@token_required
def update_pedido_status(pedido_id):
    pedido = pedido.query.get_or_404(pedido_id)
    data = request.get_json()
    
    if not data or not data.get("status"):
        return jsonify({"message": "Status é obrigatório!"}), 400
        
    # Validação de status (opcional)
    status_validos = ["EM_ABERTO", "SAIDA", "RETORNO", "FECHADO"]
    if data["status"] not in status_validos:
        return jsonify({"message": f"Status inválido! Valores permitidos: {', '.join(status_validos)}"}), 400
    
    old_status = pedido.status
    pedido.status = data["status"]
    
    try:
        db.session.commit()
        register_log("UPDATE", "Pedido", pedido.id, f"Status alterado: {old_status} -> {pedido.status}")
        return jsonify({"message": "Status do pedido atualizado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao atualizar status do pedido {pedido_id}: {e}")
        return jsonify({"message": "Erro interno ao atualizar status do pedido."}), 500
