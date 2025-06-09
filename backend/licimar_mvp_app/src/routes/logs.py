from flask import Blueprint, jsonify, request, current_app
from src.models.log import Log
from src.models.user import User
from src.utils.decorators import role_required
from datetime import datetime, timedelta

logs_bp = Blueprint("logs", __name__)

# Rota para listar logs (apenas para admin)
@logs_bp.route("", methods=["GET"])
@role_required("admin")
def get_logs():
    try:
        # Parâmetros de filtro opcionais
        dias = request.args.get("dias", default=7, type=int)
        action = request.args.get("action", default=None, type=str)
        entity_type = request.args.get("entity_type", default=None, type=str)
        user_id = request.args.get("user_id", default=None, type=int)
        
        # Data de início para filtrar (padrão: últimos 7 dias)
        data_inicio = datetime.utcnow() - timedelta(days=dias)
        
        # Constrói a query base
        query = log.query.filter(log.created_at >= data_inicio)
        
        # Aplica filtros adicionais se fornecidos
        if action:
            query = query.filter(log.action == action)
        if entity_type:
            query = query.filter(log.entity_type == entity_type)
        if user_id:
            query = query.filter(log.user_id == user_id)
            
        # Ordena por data de criação (mais recente primeiro)
        logs = query.order_by(log.created_at.desc()).all()
        
        # Formata a resposta
        output = []
        for log in logs:
            # Busca o nome do usuário se disponível
            username = None
            if log.user_id:
                user = user.query.get(log.user_id)
                username = user.username if user else None
                
            output.append({
                "id": log.id,
                "user_id": log.user_id,
                "username": username,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.strftime("%d/%m/%Y %H:%M:%S")
            })
            
        return jsonify(output), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar logs: {e}")
        return jsonify({"message": "Erro ao buscar logs."}), 500
