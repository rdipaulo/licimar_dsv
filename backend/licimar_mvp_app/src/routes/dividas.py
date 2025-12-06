"""
Rotas para gerenciamento de dívidas e cobranças
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from ..models import Cliente, Divida, PagamentoDivida
from ..database import db
from ..utils.decorators import token_required, admin_required, log_action
from ..utils.helpers import paginate_query

dividas_bp = Blueprint('dividas', __name__)


# ============================================================================
# ENDPOINT 1: GET /api/clientes/{id}/divida-pendente
# Retorna o saldo devedor atual do cliente
# ============================================================================

@dividas_bp.route('/clientes/<int:cliente_id>/divida-pendente', methods=['GET'])
@token_required
def get_divida_pendente(cliente_id):
    """
    Retorna o saldo devedor total do cliente.
    
    Fórmula:
    Dívida Pendente Total = Σ(dividas.valor_divida) - Σ(pagamentos_divida.cobranca_divida)
    
    Args:
        cliente_id: ID do cliente
        
    Returns:
        {
            "cliente_id": int,
            "divida_total": float,
            "cobrancas_total": float,
            "saldo_devedor": float,
            "quantidade_dividas": int,
            "dividas": [
                {
                    "id_divida": int,
                    "valor_divida": float,
                    "valor_pago": float,
                    "status": str,
                    "data_registro": str
                }
            ]
        }
    """
    try:
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({'message': 'Cliente não encontrado'}), 404
        
        # Utiliza a property divida_pendente_total do Cliente
        saldo_devedor = cliente.divida_pendente_total
        
        # Busca todas as dívidas do cliente
        dividas = Divida.query.filter_by(id_cliente=cliente_id).all()
        
        # Calcula totais
        divida_total = sum(d.valor_divida for d in dividas) if dividas else 0.0
        
        # Calcula pagamentos por dívida
        dividas_detail = []
        for divida in dividas:
            pagamentos = PagamentoDivida.query.filter_by(id_divida=divida.id_divida).all()
            valor_pago = sum(p.cobranca_divida for p in pagamentos) if pagamentos else 0.0
            
            dividas_detail.append({
                'id_divida': divida.id_divida,
                'valor_divida': divida.valor_divida,
                'valor_pago': valor_pago,
                'saldo': divida.valor_divida - valor_pago,
                'descricao': divida.descricao,
                'status': divida.status,
                'data_registro': divida.data_registro.isoformat() if divida.data_registro else None
            })
        
        cobrancas_total = sum(d['valor_pago'] for d in dividas_detail)
        
        return jsonify({
            'cliente_id': cliente_id,
            'cliente_nome': cliente.nome,
            'divida_total': divida_total,
            'cobrancas_total': cobrancas_total,
            'saldo_devedor': saldo_devedor,
            'quantidade_dividas': len(dividas_detail),
            'dividas': dividas_detail
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter dívida pendente: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500


# ============================================================================
# ENDPOINT 2: POST /api/dividas/registrar
# Registra um novo débito (lançamento de dívida)
# ============================================================================

@dividas_bp.route('/registrar', methods=['POST'])
@token_required
@log_action('REGISTRAR_DIVIDA')
def registrar_divida():
    """
    Registra um novo débito para um cliente.
    
    Body:
    {
        "id_cliente": int (obrigatório),
        "valor_divida": float (obrigatório, > 0),
        "descricao": str (opcional),
        "id_pedido": int (opcional - referência ao pedido)
    }
    
    Returns:
        {
            "message": "Dívida registrada com sucesso",
            "id_divida": int,
            "id_cliente": int,
            "valor_divida": float,
            "status": "Em Aberto",
            "data_registro": str
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Validações
        id_cliente = data.get('id_cliente')
        valor_divida = data.get('valor_divida')
        
        if not id_cliente:
            return jsonify({'message': 'id_cliente é obrigatório'}), 400
        
        if not valor_divida:
            return jsonify({'message': 'valor_divida é obrigatório'}), 400
        
        # Validação do cliente
        cliente = Cliente.query.get(id_cliente)
        if not cliente:
            return jsonify({'message': 'Cliente não encontrado'}), 404
        
        # Validação do valor
        try:
            valor_divida = float(valor_divida)
            if valor_divida <= 0:
                return jsonify({'message': 'valor_divida deve ser maior que 0'}), 400
        except ValueError:
            return jsonify({'message': 'valor_divida deve ser um número válido'}), 400
        
        # Cria novo registro de dívida
        nova_divida = Divida(
            id_cliente=id_cliente,
            data_registro=datetime.now(),
            valor_divida=valor_divida,
            descricao=data.get('descricao', 'Débito registrado'),
            status='Em Aberto'
        )
        
        db.session.add(nova_divida)
        db.session.commit()
        
        current_app.logger.info(f"Dívida registrada: Cliente {id_cliente}, Valor R${valor_divida}")
        
        return jsonify({
            'message': 'Dívida registrada com sucesso',
            'id_divida': nova_divida.id_divida,
            'id_cliente': nova_divida.id_cliente,
            'valor_divida': nova_divida.valor_divida,
            'status': nova_divida.status,
            'data_registro': nova_divida.data_registro.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao registrar dívida: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500


# ============================================================================
# ENDPOINT 3: POST /api/pagamentos-divida/registrar
# Registra um pagamento/cobrança (abatimento de dívida)
# ============================================================================

@dividas_bp.route('/pagamentos-divida/registrar', methods=['POST'])
@token_required
@log_action('REGISTRAR_PAGAMENTO_DIVIDA')
def registrar_pagamento_divida():
    """
    Registra um pagamento/cobrança (abatimento) de uma dívida.
    
    Lógica:
    - Se o valor for suficiente para quitar a dívida mais antiga, marca como quitada
    - Se restar saldo, cria uma dívida nova com o saldo remanescente
    - Atualiza o status da dívida para 'Parcialmente Pago' ou 'Quitado'
    
    Body:
    {
        "id_cliente": int (obrigatório),
        "cobranca_divida": float (obrigatório, > 0),
        "descricao": str (opcional),
        "id_pedido": int (opcional - referência ao pedido de retorno)
    }
    
    Returns:
        {
            "message": "Pagamento registrado com sucesso",
            "id_lancamento": int,
            "id_cliente": int,
            "cobranca_divida": float,
            "dividas_quitadas": int,
            "saldo_devedor_novo": float,
            "data_pagamento": str
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Validações
        id_cliente = data.get('id_cliente')
        cobranca_divida = data.get('cobranca_divida')
        
        if not id_cliente:
            return jsonify({'message': 'id_cliente é obrigatório'}), 400
        
        if not cobranca_divida:
            return jsonify({'message': 'cobranca_divida é obrigatório'}), 400
        
        # Validação do cliente
        cliente = Cliente.query.get(id_cliente)
        if not cliente:
            return jsonify({'message': 'Cliente não encontrado'}), 404
        
        # Validação do valor
        try:
            cobranca_divida = float(cobranca_divida)
            if cobranca_divida <= 0:
                return jsonify({'message': 'cobranca_divida deve ser maior que 0'}), 400
        except ValueError:
            return jsonify({'message': 'cobranca_divida deve ser um número válido'}), 400
        
        # Busca dívidas abertas do cliente, ordenadas por data (mais antiga primeiro)
        dividas_abertas = Divida.query.filter(
            Divida.id_cliente == id_cliente,
            Divida.status.in_(['Em Aberto', 'Parcialmente Pago'])
        ).order_by(Divida.data_registro).all()
        
        if not dividas_abertas:
            return jsonify({'message': 'Cliente não possui dívidas em aberto'}), 400
        
        # Processa o abatimento
        valor_restante = cobranca_divida
        dividas_quitadas = 0
        
        for divida in dividas_abertas:
            if valor_restante <= 0:
                break
            
            # Calcula quanto já foi pago dessa dívida
            pagamentos_anteriores = PagamentoDivida.query.filter_by(id_divida=divida.id_divida).all()
            valor_ja_pago = sum(p.cobranca_divida for p in pagamentos_anteriores) if pagamentos_anteriores else 0.0
            
            saldo_devedor = divida.valor_divida - valor_ja_pago
            
            # Aplica o abatimento
            if valor_restante >= saldo_devedor:
                # Quitação completa dessa dívida
                valor_abatido = saldo_devedor
                divida.status = 'Quitado'
                dividas_quitadas += 1
            else:
                # Abatimento parcial
                valor_abatido = valor_restante
                divida.status = 'Parcialmente Pago'
            
            # Registra o pagamento
            pagamento = PagamentoDivida(
                id_divida=divida.id_divida,
                data_pagamento=datetime.now(),
                cobranca_divida=valor_abatido,
                descricao=data.get('descricao', 'Cobrança de dívida')
            )
            
            db.session.add(pagamento)
            valor_restante -= valor_abatido
        
        # Se sobrar saldo e não houver mais dívidas a pagar, não faz nada
        # (o saldo extra não é registrado como crédito por enquanto)
        
        db.session.commit()
        
        # Calcula novo saldo devedor
        saldo_novo = cliente.divida_pendente_total
        
        current_app.logger.info(
            f"Pagamento registrado: Cliente {id_cliente}, "
            f"Cobrança R${cobranca_divida}, Dívidas quitadas: {dividas_quitadas}"
        )
        
        return jsonify({
            'message': 'Pagamento registrado com sucesso',
            'id_cliente': id_cliente,
            'cobranca_divida': cobranca_divida,
            'dividas_quitadas': dividas_quitadas,
            'saldo_devedor_novo': saldo_novo,
            'data_pagamento': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao registrar pagamento de dívida: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500


# ============================================================================
# ENDPOINT ADICIONAL: GET /api/dividas
# Lista todas as dívidas com filtros
# ============================================================================

@dividas_bp.route('', methods=['GET'])
@token_required
def get_dividas():
    """
    Lista dívidas com filtros e paginação
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', '').strip()
        cliente_id = request.args.get('cliente_id', type=int)
        
        query = Divida.query
        
        if status:
            query = query.filter(Divida.status == status)
        
        if cliente_id:
            query = query.filter(Divida.id_cliente == cliente_id)
        
        query = query.order_by(Divida.data_registro.desc())
        
        result = paginate_query(query, page, per_page)
        
        # Enriquece cada dívida com informações de pagamentos
        for item in result['items']:
            divida_dict = item.to_dict() if hasattr(item, 'to_dict') else {
                'id_divida': item.id_divida,
                'id_cliente': item.id_cliente,
                'valor_divida': item.valor_divida,
                'status': item.status,
                'data_registro': item.data_registro.isoformat() if item.data_registro else None,
                'descricao': item.descricao
            }
            
            # Calcula valor pago
            pagamentos = PagamentoDivida.query.filter_by(id_divida=item.id_divida).all()
            divida_dict['valor_pago'] = sum(p.cobranca_divida for p in pagamentos) if pagamentos else 0.0
            divida_dict['saldo'] = divida_dict['valor_divida'] - divida_dict['valor_pago']
            
            item.__dict__.update(divida_dict)
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar dívidas: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500
