"""
Rotas para gerenciamento de pedidos
"""
from flask import Blueprint, request, jsonify, current_app
from ..models import Pedido, ItemPedido, Produto, Ambulante
from ..database import db
from ..utils.decorators import token_required, admin_required, log_action
from ..utils.helpers import paginate_query, is_gelo_seco

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('', methods=['GET'])
@token_required
def get_pedidos():
    """
    Lista pedidos com paginação e filtros
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', '').strip()
        ambulante_id = request.args.get('ambulante_id', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Constrói a query base
        query = Pedido.query
        
        # Aplica filtros
        if status:
            if status == 'EM_ABERTO':
                query = query.filter(Pedido.status == 'saida')
            else:
                query = query.filter(Pedido.status == status)
        
        if ambulante_id:
            query = query.filter(Pedido.ambulante_id == ambulante_id)
        
        if data_inicio:
            try:
                from datetime import datetime
                data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
                query = query.filter(Pedido.data_operacao >= data_inicio_dt)
            except ValueError:
                return jsonify({'message': 'Data de início inválida. Use formato YYYY-MM-DD'}), 400
        
        if data_fim:
            try:
                from datetime import datetime, timedelta
                data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Pedido.data_operacao < data_fim_dt)
            except ValueError:
                return jsonify({'message': 'Data de fim inválida. Use formato YYYY-MM-DD'}), 400
        
        # Ordena por data (mais recente primeiro)
        query = query.order_by(Pedido.data_operacao.desc())
        
        # Aplica paginação
        result = paginate_query(query, page, per_page)
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar pedidos: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@pedidos_bp.route('/<int:pedido_id>', methods=['GET'])
@token_required
def get_pedido(pedido_id):
    """
    Obtém um pedido específico
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({'message': 'Pedido não encontrado'}), 404
        
        return jsonify(pedido.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter pedido: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@pedidos_bp.route('/saida', methods=['POST'])
@token_required
@log_action('CREATE_PEDIDO_SAIDA')
def criar_pedido_saida():
    """
    Cria um novo pedido de saída
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Validação dos campos obrigatórios
        ambulante_id = data.get('ambulante_id', type=int)
        if not ambulante_id:
            return jsonify({'message': 'ID do ambulante é obrigatório'}), 400
        
        # Verifica se o ambulante existe e está ativo
        ambulante = Ambulante.query.get(ambulante_id)
        if not ambulante:
            return jsonify({'message': 'Ambulante não encontrado'}), 404
        
        if ambulante.status != 'ativo':
            return jsonify({'message': 'Ambulante não está ativo'}), 400
        
        itens_saida = data.get('itens_saida', [])
        if not itens_saida:
            return jsonify({'message': 'Nenhum item adicionado ao pedido'}), 400
        
        # Cria o pedido
        pedido = Pedido(
            ambulante_id=ambulante_id,
            status='saida',
            observacoes=data.get('observacoes', '')
        )
        
        db.session.add(pedido)
        db.session.flush()  # Para obter o ID do pedido
        
        # Adiciona itens ao pedido
        total_pedido = 0
        for item_data in itens_saida:
            produto_id = item_data.get('produto_id', type=int)
            quantidade_saida = item_data.get('quantidade_saida', 0)
            
            if not produto_id or quantidade_saida <= 0:
                continue
            
            # Verifica se o produto existe
            produto = Produto.query.get(produto_id)
            if not produto or not produto.active:
                return jsonify({'message': f'Produto ID {produto_id} não encontrado ou inativo'}), 400
            
            # Converte quantidade baseado no tipo de produto
            if is_gelo_seco(produto.nome):
                try:
                    quantidade_saida = float(quantidade_saida)
                except (ValueError, TypeError):
                    quantidade_saida = 0.0
            else:
                try:
                    quantidade_saida = int(float(quantidade_saida))
                except (ValueError, TypeError):
                    quantidade_saida = 0
            
            if quantidade_saida <= 0:
                continue
            
            # Cria item do pedido
            item_pedido = ItemPedido(
                pedido_id=pedido.id,
                produto_id=produto_id,
                quantidade_saida=quantidade_saida,
                quantidade_retorno=0,
                preco_unitario=produto.preco
            )
            
            db.session.add(item_pedido)
            total_pedido += float(quantidade_saida * produto.preco)
        
        # Atualiza o total do pedido
        pedido.total = total_pedido
        
        db.session.commit()
        
        return jsonify({
            'message': 'Pedido de saída criado com sucesso',
            'pedido': pedido.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar pedido de saída: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@pedidos_bp.route('/<int:pedido_id>/retorno', methods=['POST'])
@token_required
@log_action('REGISTER_RETORNO')
def registrar_retorno(pedido_id):
    """
    Registra o retorno de um pedido
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({'message': 'Pedido não encontrado'}), 404
        
        if pedido.status != 'saida':
            return jsonify({'message': 'Pedido não está em status de saída'}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        itens_retorno = data.get('itens', [])
        
        # Atualiza quantidades de retorno
        for item_data in itens_retorno:
            produto_id = item_data.get('produto_id', type=int)
            quantidade_retorno = item_data.get('quantidade_retorno', 0)
            
            if not produto_id:
                continue
            
            # Encontra o item do pedido
            item_pedido = ItemPedido.query.filter_by(
                pedido_id=pedido_id,
                produto_id=produto_id
            ).first()
            
            if not item_pedido:
                continue
            
            # Converte quantidade baseado no tipo de produto
            produto = Produto.query.get(produto_id)
            if produto and is_gelo_seco(produto.nome):
                try:
                    quantidade_retorno = float(quantidade_retorno)
                except (ValueError, TypeError):
                    quantidade_retorno = 0.0
            else:
                try:
                    quantidade_retorno = int(float(quantidade_retorno))
                except (ValueError, TypeError):
                    quantidade_retorno = 0
            
            # Valida se a quantidade de retorno não é maior que a saída
            if quantidade_retorno > item_pedido.quantidade_saida:
                return jsonify({
                    'message': f'Quantidade de retorno não pode ser maior que a quantidade de saída para o produto {produto.nome if produto else produto_id}'
                }), 400
            
            item_pedido.quantidade_retorno = quantidade_retorno
        
        # Atualiza status do pedido
        pedido.status = 'retorno'
        
        # Recalcula o total do pedido
        pedido.calcular_total()
        
        # Adiciona observações se fornecidas
        if data.get('observacoes'):
            if pedido.observacoes:
                pedido.observacoes += f"\n\nRetorno: {data['observacoes']}"
            else:
                pedido.observacoes = f"Retorno: {data['observacoes']}"
        
        db.session.commit()
        
        return jsonify({
            'message': 'Retorno registrado com sucesso',
            'pedido': pedido.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao registrar retorno: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@pedidos_bp.route('/<int:pedido_id>/finalizar', methods=['POST'])
@token_required
@log_action('FINALIZE_PEDIDO')
def finalizar_pedido(pedido_id):
    """
    Finaliza um pedido (marca como finalizado)
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({'message': 'Pedido não encontrado'}), 404
        
        if pedido.status == 'finalizado':
            return jsonify({'message': 'Pedido já está finalizado'}), 400
        
        # Finaliza o pedido
        pedido.status = 'finalizado'
        
        # Recalcula o total final
        pedido.calcular_total()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Pedido finalizado com sucesso',
            'pedido': pedido.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao finalizar pedido: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@pedidos_bp.route('/<int:pedido_id>/itens', methods=['GET'])
@token_required
def get_pedido_itens(pedido_id):
    """
    Obtém os itens de um pedido específico
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({'message': 'Pedido não encontrado'}), 404
        
        # Retorna os itens do pedido
        itens = [item.to_dict() for item in pedido.itens]
        
        return jsonify({
            'pedido_id': pedido_id,
            'ambulante_nome': pedido.ambulante.nome,
            'status': pedido.status,
            'total': float(pedido.total),
            'itens': itens
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter itens do pedido: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@pedidos_bp.route('/<int:pedido_id>', methods=['DELETE'])
@admin_required
@log_action('DELETE_PEDIDO')
def delete_pedido(pedido_id):
    """
    Remove um pedido (apenas administradores)
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({'message': 'Pedido não encontrado'}), 404
        
        # Remove o pedido (os itens são removidos automaticamente devido ao cascade)
        db.session.delete(pedido)
        db.session.commit()
        
        return jsonify({'message': 'Pedido removido com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao remover pedido: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500
