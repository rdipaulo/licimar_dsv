from flask import Blueprint, request, jsonify, current_app, g
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
from datetime import datetime, timedelta

# Importa a instância db e os modelos necessários
from src.database import db
from src.models import user, log
# Importa a função auxiliar para registrar logs
from src.utils.helpers import register_log 

# Cria um Blueprint (um conjunto de rotas) para autenticação
auth_bp = Blueprint("auth", __name__)

# Rota para login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"message": "Nome de usuário e senha são obrigatórios!"}), 400

    user = user.query.filter_by(username=data["username"]).first()

    # Verifica se o usuário existe e a senha está correta
    if not user or not user.check_password(data["password"]):
        # Registrar tentativa de login falha (opcional, mas bom para segurança)
        # register_log("LOGIN_FAIL", "Auth", None, f"Tentativa com usuário: {data["username"]}")
        return jsonify({"message": "Credenciais inválidas!"}), 401
    
    # Verifica se o usuário está ativo
    if not user.active:
         # register_log("LOGIN_INACTIVE", "Auth", user.id, f"Tentativa com usuário inativo: {user.username}")
        return jsonify({"message": "Usuário inativo!"}), 403

    # Gera o token JWT
    try:
        token_payload = {
            "sub": user.id, # Subject (identificador do usuário)
            "role": user.role,
            "iat": datetime.utcnow(), # Issued at (quando foi gerado)
            "exp": datetime.utcnow() + timedelta(days=current_app.config.get("JWT_EXPIRATION_DAYS", 1)) # Expiration
        }
        token = jwt.encode(
            token_payload,
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )
        
        # Registrar login bem-sucedido
        # Usaremos g.user mais tarde, por enquanto passamos o ID diretamente
        # register_log("LOGIN_SUCCESS", "Auth", user.id, f"Usuário logado: {user.username}")
        
        return jsonify({
            "message": "Login bem-sucedido!",
            "token": token,
            "user": {"id": user.id, "username": user.username, "role": user.role}
        }), 200

    except Exception as e:
        current_app.logger.error(f"Erro ao gerar token JWT: {e}")
        return jsonify({"message": "Erro interno ao tentar fazer login."}), 500

# Rota para registro (exemplo básico, pode precisar de mais validações)
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password") or not data.get("email"):
        return jsonify({"message": "Nome de usuário, email e senha são obrigatórios!"}), 400

    # Verifica se usuário ou email já existem
    if user.query.filter((user.username == data["username"]) | (user.email == data["email"])).first():
        return jsonify({"message": "Nome de usuário ou email já cadastrado!"}), 409 # Conflict

    new_user = user(
        username=data["username"],
        email=data["email"],
        role=data.get("role", "user") # Padrão 'user' se não especificado
    )
    new_user.set_password(data["password"])
    
    try:
        db.session.add(new_user)
        db.session.commit()
        # Registrar criação de usuário
        # register_log("CREATE", "User", new_user.id, f"Usuário registrado: {new_user.username}")
        return jsonify({"message": "Usuário registrado com sucesso!", "user_id": new_user.id}), 201 # Created
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao registrar usuário: {e}")
        return jsonify({"message": "Erro interno ao registrar usuário."}), 500
