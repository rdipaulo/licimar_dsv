from flask import request, g, current_app
import json
from database import db
from src.models.log import Log


def register_log(action, entity_type=None, entity_id=None, details=None):
    """
    Registra uma operação no log de auditoria.
    Busca o usuário logado a partir de g.user (definido por @token_required).
    """
    user_id = None
    # Verifica se g.user existe e tem um id
    if hasattr(g, "user") and g.user and hasattr(g.user, "id"):
        user_id = g.user.id
    # Se não houver usuário em g, não registra o log ou registra como ação do sistema?
    # Por enquanto, só registra se houver usuário.
    elif action.startswith("LOGIN") or action.startswith("REGISTER"): 
         # Para login/registro, podemos pegar o ID do usuário recém-criado/logado se disponível
         # Mas a forma mais simples é garantir que o decorator coloque o usuário em 'g'
         # ou passar o user_id explicitamente para register_log nesses casos.
         # Vamos simplificar: logs só com usuário autenticado (exceto falhas de login talvez)
         pass # Não registra se não houver g.user, exceto talvez falhas
    else:
         # Não registra outras ações se não houver usuário logado
         # current_app.logger.warning(f"Tentativa de log sem usuário autenticado: {action}")
         return 

    # Converte detalhes para JSON se for um dicionário
    details_json = None
    if isinstance(details, dict):
        try:
            details_json = json.dumps(details, ensure_ascii=False)
        except TypeError:
            details_json = json.dumps(str(details)) # Fallback para string
    elif isinstance(details, str):
        details_json = details

    log_entry = Log(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details_json,
        ip_address=request.remote_addr # Pega o IP da requisição
    )
    
    try:
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Logar o erro no log da aplicação, não no banco de logs
        current_app.logger.error(f"Erro ao salvar log no banco: {e}")
    