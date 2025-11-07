"""
Rotas para visualização de logs do sistema
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from models import Log, User
from database import db
from utils.decorators import admin_required
from utils.helpers import paginate_query

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('', methods=['GET'])
@admin_required
def get_logs():
    """
    Lista logs do sistema com paginação e filtros
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        user_id = request.args.get('user_id', type=int)
        action = request.args.get('action', '').strip()
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Constrói a query base
        query = Log.query
        
        # Aplica filtros
        if user_id:
            query = query.filter(Log.user_id == user_id)
        
        if action:
            query = query.filter(Log.action.ilike(f'%{action}%'))
        
        if data_inicio:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
                query = query.filter(Log.created_at >= data_inicio_dt)
            except ValueError:
                return jsonify({'message': 'Data de início inválida. Use formato YYYY-MM-DD'}), 400
        
        if data_fim:
            try:
                data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Log.created_at < data_fim_dt)
            except ValueError:
                return jsonify({'message': 'Data de fim inválida. Use formato YYYY-MM-DD'}), 400
        
        # Ordena por data (mais recente primeiro)
        query = query.order_by(Log.created_at.desc())
        
        # Aplica paginação
        result = paginate_query(query, page, per_page)
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar logs: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@logs_bp.route('/<int:log_id>', methods=['GET'])
@admin_required
def get_log(log_id):
    """
    Obtém um log específico
    """
    try:
        log = Log.query.get(log_id)
        
        if not log:
            return jsonify({'message': 'Log não encontrado'}), 404
        
        return jsonify(log.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter log: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@logs_bp.route('/actions', methods=['GET'])
@admin_required
def get_log_actions():
    """
    Lista todas as ações disponíveis nos logs (para filtros)
    """
    try:
        actions = db.session.query(Log.action).distinct().order_by(Log.action).all()
        action_list = [action[0] for action in actions if action[0]]
        
        return jsonify(action_list), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar ações de log: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@logs_bp.route('/users', methods=['GET'])
@admin_required
def get_log_users():
    """
    Lista usuários que têm logs (para filtros)
    """
    try:
        users = db.session.query(
            User.id,
            User.username
        ).join(
            Log, User.id == Log.user_id
        ).distinct().order_by(User.username).all()
        
        user_list = [{'id': user.id, 'username': user.username} for user in users]
        
        return jsonify(user_list), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar usuários com logs: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@logs_bp.route('/stats', methods=['GET'])
@admin_required
def get_log_stats():
    """
    Estatísticas dos logs
    """
    try:
        # Total de logs
        total_logs = Log.query.count()
        
        # Logs de hoje
        hoje = datetime.now().date()
        logs_hoje = Log.query.filter(
            db.func.date(Log.created_at) == hoje
        ).count()
        
        # Logs dos últimos 7 dias
        uma_semana_atras = datetime.now() - timedelta(days=7)
        logs_semana = Log.query.filter(
            Log.created_at >= uma_semana_atras
        ).count()
        
        # Ações mais comuns (top 10)
        acoes_comuns = db.session.query(
            Log.action,
            db.func.count(Log.id).label('count')
        ).group_by(
            Log.action
        ).order_by(
            db.func.count(Log.id).desc()
        ).limit(10).all()
        
        acoes_list = [
            {'action': acao.action, 'count': acao.count}
            for acao in acoes_comuns
        ]
        
        # Usuários mais ativos (top 10)
        usuarios_ativos = db.session.query(
            User.username,
            db.func.count(Log.id).label('count')
        ).join(
            Log, User.id == Log.user_id
        ).group_by(
            User.id, User.username
        ).order_by(
            db.func.count(Log.id).desc()
        ).limit(10).all()
        
        usuarios_list = [
            {'username': usuario.username, 'count': usuario.count}
            for usuario in usuarios_ativos
        ]
        
        return jsonify({
            'total_logs': total_logs,
            'logs_hoje': logs_hoje,
            'logs_semana': logs_semana,
            'acoes_mais_comuns': acoes_list,
            'usuarios_mais_ativos': usuarios_list
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter estatísticas de logs: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@logs_bp.route('/cleanup', methods=['POST'])
@admin_required
def cleanup_logs():
    """
    Remove logs antigos (mais de X dias)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        try:
            dias = int(data.get('dias', 90))
            if dias <= 0:
                return jsonify({'message': 'Número de dias deve ser maior que zero'}), 400
        except (ValueError, TypeError):
            return jsonify({'message': 'Número de dias inválido'}), 400
        
        # Data limite
        data_limite = datetime.now() - timedelta(days=dias)
        
        # Conta logs a serem removidos
        logs_para_remover = Log.query.filter(Log.created_at < data_limite).count()
        
        if logs_para_remover == 0:
            return jsonify({
                'message': f'Nenhum log encontrado com mais de {dias} dias'
            }), 200
        
        # Remove os logs
        Log.query.filter(Log.created_at < data_limite).delete()
        db.session.commit()
        
        return jsonify({
            'message': f'{logs_para_remover} logs removidos com sucesso',
            'logs_removidos': logs_para_remover,
            'data_limite': data_limite.isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao limpar logs: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500
