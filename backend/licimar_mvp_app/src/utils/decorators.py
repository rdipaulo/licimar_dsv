from functools import wraps
from flask import request, jsonify, current_app, g
import jwt
from src.models.user import User

# Decorator para exigir um token JWT válido
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Tenta pegar o token do cabeçalho Authorization (formato Bearer <token>)
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token não fornecido!"}), 401

        try:
            # Decodifica o token usando a SECRET_KEY da aplicação
            data = jwt.decode(
                token, 
                current_app.config["SECRET_KEY"], 
                algorithms=["HS256"]
            )
            # Busca o usuário no banco de dados pelo ID (sub) contido no token
            current_user = User.query.filter_by(id=data["sub"]).first()
            
            if not current_user:
                return jsonify({"message": "Usuário do token não encontrado!"}), 401
            
            if not current_user.active:
                 return jsonify({"message": "Usuário inativo!"}), 403

            # Armazena o usuário e o papel no objeto 'g' do Flask
            # 'g' é um objeto especial que dura apenas por uma requisição
            g.user = current_user
            g.role = data["role"]

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expirado!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token inválido!"}), 401
        except Exception as e:
            current_app.logger.error(f"Erro na validação do token: {e}")
            return jsonify({"message": "Erro ao processar o token."}), 500

        # Se tudo deu certo, chama a função original da rota
        return f(*args, **kwargs)
    return decorated

# Decorator para exigir um papel (role) específico
def role_required(roles):
    # roles deve ser uma lista ou tupla, ex: ["admin"] ou ["admin", "manager"]
    if not isinstance(roles, (list, tuple)):
        roles = [roles] # Garante que seja uma lista
        
    def decorator(f):
        @wraps(f)
        # Garante que @token_required seja usado ANTES deste decorator
        @token_required 
        def decorated_function(*args, **kwargs):
            # Verifica se o @token_required colocou o usuário e o papel em 'g'
            if not hasattr(g, "user") or not hasattr(g, "role"):
                # Isso não deveria acontecer se @token_required foi usado corretamente
                return jsonify({"message": "Erro interno: contexto de autenticação ausente."}), 500
            
            # Verifica se o papel do usuário está na lista de papéis permitidos
            if g.role not in roles:
                return jsonify({"message": f"Acesso negado! Requer papel(éis): {', '.join(roles)}"}), 403 # Forbidden
            
            # Se o papel for permitido, chama a função original da rota
            return f(*args, **kwargs)
        return decorated_function
    return decorator
