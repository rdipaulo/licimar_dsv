"""
Funções auxiliares e utilitários
"""
import re
from datetime import datetime
import pytz
from flask import request, current_app
from ..database import db

# Timezone de Brasília
TZ_BRASILIA = pytz.timezone('America/Sao_Paulo')

def get_brasilia_now():
    """
    Retorna data/hora atual em Brasília
    """
    return datetime.now(TZ_BRASILIA).replace(tzinfo=None)

def validate_email(email):
    """
    Valida formato de email
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_cpf(cpf):
    """
    Valida CPF brasileiro
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    dv1 = 0 if resto < 2 else 11 - resto
    
    # Calcula o segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    dv2 = 0 if resto < 2 else 11 - resto
    
    # Verifica se os dígitos verificadores estão corretos
    return cpf[9] == str(dv1) and cpf[10] == str(dv2)

def validate_phone(phone):
    """
    Valida telefone brasileiro
    """
    # Remove caracteres não numéricos
    phone = re.sub(r'[^0-9]', '', phone)
    
    # Verifica se tem 10 ou 11 dígitos (com DDD)
    return len(phone) in [10, 11]

def format_currency(value):
    """
    Formata valor monetário para exibição
    """
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def sanitize_string(text):
    """
    Sanitiza string removendo caracteres perigosos
    """
    if not text:
        return text
    
    # Remove tags HTML básicas
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove caracteres de controle
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return text.strip()

def register_log(user_id, action, details=None):
    """
    Registra uma ação no log do sistema
    """
    try:
        from ..models import Log
        log_entry = Log(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr if request else None,
            user_agent=request.user_agent.string if request else None
        )
        db.session.add(log_entry)
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao registrar log: {e}")
        return False

def calcular_desconto_cobranca(valor_pago):
    """
    Calcula o desconto/cobrança baseado nas regras configuradas
    """
    try:
        from ..models import RegraCobranca
        # Busca a regra aplicável ao valor pago
        regra = RegraCobranca.query.filter(
            RegraCobranca.faixa_inicial <= valor_pago,
            RegraCobranca.faixa_final >= valor_pago,
            RegraCobranca.active == True
        ).first()
        
        if regra:
            desconto = valor_pago * (float(regra.percentual) / 100)
            return {
                'regra_id': regra.id,
                'percentual': float(regra.percentual),
                'desconto': desconto,
                'valor_final': valor_pago - desconto,
                'descricao': regra.descricao
            }
        
        # Se não encontrar regra, retorna sem desconto
        return {
            'regra_id': None,
            'percentual': 0,
            'desconto': 0,
            'valor_final': valor_pago,
            'descricao': 'Nenhuma regra aplicável'
        }
    except Exception as e:
        current_app.logger.error(f"Erro ao calcular desconto: {e}")
        return {
            'regra_id': None,
            'percentual': 0,
            'desconto': 0,
            'valor_final': valor_pago,
            'descricao': 'Erro no cálculo'
        }

def paginate_query(query, page=1, per_page=20):
    """
    Aplica paginação a uma query
    """
    try:
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 20
        
        # Limita o número de itens por página
        per_page = min(per_page, 100)
        
        paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'items': [item.to_dict() for item in paginated.items],
            'pagination': {
                'page': paginated.page,
                'pages': paginated.pages,
                'per_page': paginated.per_page,
                'total': paginated.total,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev,
                'next_num': paginated.next_num,
                'prev_num': paginated.prev_num
            }
        }
    except Exception as e:
        current_app.logger.error(f"Erro na paginação: {e}")
        return {
            'items': [],
            'pagination': {
                'page': 1,
                'pages': 0,
                'per_page': per_page,
                'total': 0,
                'has_next': False,
                'has_prev': False,
                'next_num': None,
                'prev_num': None
            }
        }

def generate_report_filename(report_type, format_type='pdf'):
    """
    Gera nome de arquivo para relatórios
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"licimar_{report_type}_{timestamp}.{format_type}"

def is_gelo_seco(produto_nome):
    """
    Verifica se um produto é gelo seco (permite quantidades decimais)
    """
    return 'gelo' in produto_nome.lower() and 'seco' in produto_nome.lower()
