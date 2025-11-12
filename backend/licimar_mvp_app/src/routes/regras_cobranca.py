"""
Rotas para gerenciamento de regras de cobrança de dívida
"""
from flask import Blueprint, request, jsonify, current_app
from ..models import RegraCobranca
from ..database import db
from ..utils.decorators import admin_required, log_action
from ..utils.helpers import sanitize_string, paginate_query, calcular_desconto_cobranca

regras_cobranca_bp = Blueprint('regras_cobranca', __name__)

@regras_cobranca_bp.route('', methods=['GET'])
@admin_required
def get_regras_cobranca():
    """
    Lista todas as regras de cobrança com paginação e filtros
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        active_only = request.args.get('active_only', True, type=bool)
        
        # Constrói a query base
        query = RegraCobranca.query
        
        # Aplica filtros
        if active_only:
            query = query.filter(RegraCobranca.active == True)
        
        # Ordena por faixa inicial
        query = query.order_by(RegraCobranca.faixa_inicial)
        
        # Aplica paginação
        result = paginate_query(query, page, per_page)
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar regras de cobrança: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@regras_cobranca_bp.route('/<int:regra_id>', methods=['GET'])
@admin_required
def get_regra_cobranca(regra_id):
    """
    Obtém uma regra de cobrança específica
    """
    try:
        regra = RegraCobranca.query.get(regra_id)
        
        if not regra:
            return jsonify({'message': 'Regra de cobrança não encontrada'}), 404
        
        return jsonify(regra.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter regra de cobrança: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@regras_cobranca_bp.route('', methods=['POST'])
@admin_required
@log_action('CREATE_REGRA_COBRANCA')
def create_regra_cobranca():
    """
    Cria uma nova regra de cobrança
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Validação dos campos obrigatórios
        try:
            faixa_inicial = float(data.get('faixa_inicial', 0))
            if faixa_inicial < 0:
                return jsonify({'message': 'Faixa inicial não pode ser negativa'}), 400
        except (ValueError, TypeError):
            return jsonify({'message': 'Faixa inicial inválida'}), 400
        
        try:
            faixa_final = float(data.get('faixa_final', 0))
            if faixa_final < 0:
                return jsonify({'message': 'Faixa final não pode ser negativa'}), 400
        except (ValueError, TypeError):
            return jsonify({'message': 'Faixa final inválida'}), 400
        
        if faixa_final <= faixa_inicial:
            return jsonify({'message': 'Faixa final deve ser maior que a faixa inicial'}), 400
        
        try:
            percentual = float(data.get('percentual', 0))
            if percentual < 0 or percentual > 100:
                return jsonify({'message': 'Percentual deve estar entre 0 e 100'}), 400
        except (ValueError, TypeError):
            return jsonify({'message': 'Percentual inválido'}), 400
        
        # Validação dos campos opcionais
        descricao = sanitize_string(data.get('descricao', '').strip()) if data.get('descricao') else None
        
        # Verifica se há sobreposição com outras regras ativas
        overlapping_rule = RegraCobranca.query.filter(
            RegraCobranca.active == True,
            RegraCobranca.faixa_inicial < faixa_final,
            RegraCobranca.faixa_final > faixa_inicial
        ).first()
        
        if overlapping_rule:
            return jsonify({
                'message': f'Faixa de valores se sobrepõe com regra existente: '
                          f'R$ {overlapping_rule.faixa_inicial} - R$ {overlapping_rule.faixa_final}'
            }), 409
        
        # Cria a regra
        regra = RegraCobranca(
            faixa_inicial=faixa_inicial,
            faixa_final=faixa_final,
            percentual=percentual,
            descricao=descricao
        )
        
        db.session.add(regra)
        db.session.commit()
        
        return jsonify({
            'message': 'Regra de cobrança criada com sucesso',
            'regra': regra.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar regra de cobrança: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@regras_cobranca_bp.route('/<int:regra_id>', methods=['PUT'])
@admin_required
@log_action('UPDATE_REGRA_COBRANCA')
def update_regra_cobranca(regra_id):
    """
    Atualiza uma regra de cobrança existente
    """
    try:
        regra = RegraCobranca.query.get(regra_id)
        
        if not regra:
            return jsonify({'message': 'Regra de cobrança não encontrada'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Atualiza os campos fornecidos
        if 'faixa_inicial' in data:
            try:
                faixa_inicial = float(data['faixa_inicial'])
                if faixa_inicial < 0:
                    return jsonify({'message': 'Faixa inicial não pode ser negativa'}), 400
                regra.faixa_inicial = faixa_inicial
            except (ValueError, TypeError):
                return jsonify({'message': 'Faixa inicial inválida'}), 400
        
        if 'faixa_final' in data:
            try:
                faixa_final = float(data['faixa_final'])
                if faixa_final < 0:
                    return jsonify({'message': 'Faixa final não pode ser negativa'}), 400
                regra.faixa_final = faixa_final
            except (ValueError, TypeError):
                return jsonify({'message': 'Faixa final inválida'}), 400
        
        # Valida se faixa final é maior que inicial
        if regra.faixa_final <= regra.faixa_inicial:
            return jsonify({'message': 'Faixa final deve ser maior que a faixa inicial'}), 400
        
        if 'percentual' in data:
            try:
                percentual = float(data['percentual'])
                if percentual < 0 or percentual > 100:
                    return jsonify({'message': 'Percentual deve estar entre 0 e 100'}), 400
                regra.percentual = percentual
            except (ValueError, TypeError):
                return jsonify({'message': 'Percentual inválido'}), 400
        
        if 'descricao' in data:
            regra.descricao = sanitize_string(data['descricao'].strip()) if data['descricao'] else None
        
        if 'active' in data:
            regra.active = bool(data['active'])
        
        # Verifica sobreposição apenas se a regra estiver ativa
        if regra.active:
            overlapping_rule = RegraCobranca.query.filter(
                RegraCobranca.active == True,
                RegraCobranca.id != regra_id,
                RegraCobranca.faixa_inicial < regra.faixa_final,
                RegraCobranca.faixa_final > regra.faixa_inicial
            ).first()
            
            if overlapping_rule:
                return jsonify({
                    'message': f'Faixa de valores se sobrepõe com regra existente: '
                              f'R$ {overlapping_rule.faixa_inicial} - R$ {overlapping_rule.faixa_final}'
                }), 409
        
        db.session.commit()
        
        return jsonify({
            'message': 'Regra de cobrança atualizada com sucesso',
            'regra': regra.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar regra de cobrança: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@regras_cobranca_bp.route('/<int:regra_id>', methods=['DELETE'])
@admin_required
@log_action('DELETE_REGRA_COBRANCA')
def delete_regra_cobranca(regra_id):
    """
    Remove uma regra de cobrança
    """
    try:
        regra = RegraCobranca.query.get(regra_id)
        
        if not regra:
            return jsonify({'message': 'Regra de cobrança não encontrada'}), 404
        
        db.session.delete(regra)
        db.session.commit()
        
        return jsonify({'message': 'Regra de cobrança removida com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao remover regra de cobrança: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@regras_cobranca_bp.route('/calcular', methods=['POST'])
@admin_required
def calcular_desconto():
    """
    Calcula o desconto baseado no valor pago
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        try:
            valor_pago = float(data.get('valor_pago', 0))
            if valor_pago <= 0:
                return jsonify({'message': 'Valor pago deve ser maior que zero'}), 400
        except (ValueError, TypeError):
            return jsonify({'message': 'Valor pago inválido'}), 400
        
        # Calcula o desconto usando a função helper
        resultado = calcular_desconto_cobranca(valor_pago)
        
        return jsonify({
            'valor_pago': valor_pago,
            'calculo': resultado
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao calcular desconto: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@regras_cobranca_bp.route('/ativas', methods=['GET'])
@admin_required
def get_regras_ativas():
    """
    Lista apenas regras ativas (ordenadas por faixa inicial)
    """
    try:
        regras = RegraCobranca.query.filter_by(active=True).order_by(RegraCobranca.faixa_inicial).all()
        
        return jsonify([regra.to_dict() for regra in regras]), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar regras ativas: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500
