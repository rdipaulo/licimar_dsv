"""
Rotas para gerenciamento de pedidos
"""
from flask import Blueprint, request, jsonify, current_app, render_template, make_response
from ..models import Pedido, ItemPedido, Produto, Cliente
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
        cliente_id = request.args.get('cliente_id', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = Pedido.query
        
        if status:
            if status == 'EM_ABERTO':
                query = query.filter(Pedido.status == 'saida')
            else:
                query = query.filter(Pedido.status == status)
        
        if cliente_id:
            query = query.filter(Pedido.cliente_id == cliente_id)
        
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
        
        query = query.order_by(Pedido.data_operacao.desc())
        
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
        
        cliente_id = data.get('cliente_id')
        if not cliente_id:
            return jsonify({'message': 'ID do cliente é obrigatório'}), 400
        
        cliente = Cliente.query.get(cliente_id)
        if not cliente or cliente.status != 'ativo':
            return jsonify({'message': 'Cliente não encontrado ou inativo'}), 400
        
        itens_saida = data.get('itens_saida', [])
        if not itens_saida:
            return jsonify({'message': 'Nenhum item adicionado ao pedido'}), 400
        
        pedido = Pedido(
            cliente_id=cliente_id,
            status='saida',
            observacoes=data.get('observacoes', '')
        )
        
        db.session.add(pedido)
        db.session.flush()
        
        total_pedido = 0
        for item_data in itens_saida:
            produto_id = item_data.get('produto_id')
            quantidade_saida = item_data.get('quantidade_saida', 0)
            
            if not produto_id or quantidade_saida <= 0:
                continue
            
            produto = Produto.query.get(produto_id)
            if not produto or not produto.active:
                return jsonify({'message': f'Produto ID {produto_id} não encontrado ou inativo'}), 400
            
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
            
            item_pedido = ItemPedido(
                pedido_id=pedido.id,
                produto_id=produto_id,
                quantidade_saida=quantidade_saida,
                quantidade_retorno=0,
                preco_unitario=produto.preco
            )
            
            db.session.add(item_pedido)
            total_pedido += float(quantidade_saida) * float(produto.preco)
        
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

@pedidos_bp.route('/<int:pedido_id>/saida', methods=['PUT'])
@token_required
@log_action('UPDATE_PEDIDO_SAIDA')
def atualizar_pedido_saida(pedido_id):
    """
    Atualiza um pedido de saída em aberto (status 'saida')
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({'message': 'Pedido não encontrado'}), 404
        
        if pedido.status != 'saida':
            return jsonify({'message': 'Pedido não está em status de saída e não pode ser atualizado'}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        itens_saida = data.get('itens_saida', [])
        if not itens_saida:
            return jsonify({'message': 'Nenhum item adicionado ao pedido'}), 400
        
        ItemPedido.query.filter_by(pedido_id=pedido_id).delete()
        db.session.flush()
        
        total_pedido = 0
        for item_data in itens_saida:
            produto_id = item_data.get('produto_id')
            quantidade_saida = item_data.get('quantidade_saida', 0)
            
            if not produto_id or quantidade_saida <= 0:
                continue
            
            produto = Produto.query.get(produto_id)
            if not produto or not produto.active:
                return jsonify({'message': f'Produto ID {produto_id} não encontrado ou inativo'}), 400
            
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
            
            item_pedido = ItemPedido(
                pedido_id=pedido.id,
                produto_id=produto_id,
                quantidade_saida=quantidade_saida,
                quantidade_retorno=0,
                preco_unitario=produto.preco
            )
            
            db.session.add(item_pedido)
            total_pedido += float(quantidade_saida) * float(produto.preco)
        
        from ..models import get_brasilia_now
        pedido.total = total_pedido
        pedido.observacoes = data.get('observacoes', pedido.observacoes)
        pedido.updated_at = get_brasilia_now()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Pedido de saída atualizado com sucesso',
            'pedido': pedido.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar pedido de saída: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@pedidos_bp.route('/<int:pedido_id>/retorno', methods=['POST'])
@token_required
@log_action('CREATE_PEDIDO_RETORNO')
def criar_pedido_retorno(pedido_id):
    """
    Cria um novo pedido de retorno
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({'message': 'Pedido não encontrado'}), 404
        
        if pedido.status != 'saida':
            return jsonify({'message': 'Apenas pedidos com status "saida" podem ter retorno'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        itens_retorno = data.get('itens', [])
        divida = data.get('divida', 0.0)
        
        for item_data in itens_retorno:
            produto_id = item_data.get('produto_id')
            quantidade_retorno = item_data.get('quantidade_retorno', 0)
            
            if not produto_id:
                continue
            
            # Encontra o ItemPedido correspondente
            item_pedido = ItemPedido.query.filter_by(pedido_id=pedido_id, produto_id=produto_id).first()
            
            if not item_pedido:
                return jsonify({'message': f'Produto ID {produto_id} não encontrado neste pedido'}), 400
            
            produto = item_pedido.produto
            if produto.nao_devolve:
                continue

            if is_gelo_seco(produto.nome):
                try:
                    quantidade_retorno = float(quantidade_retorno)
                except (ValueError, TypeError):
                    quantidade_retorno = 0.0
            else:
                try:
                    quantidade_retorno = int(float(quantidade_retorno))
                except (ValueError, TypeError):
                    quantidade_retorno = 0

            if quantidade_retorno < 0:
                quantidade_retorno = 0
            
            if quantidade_retorno > item_pedido.quantidade_saida:
                return jsonify({'message': f'Quantidade de retorno para {produto.nome} não pode ser maior que a de saída ({item_pedido.quantidade_saida})'}), 400
            
            item_pedido.quantidade_retorno = quantidade_retorno
            db.session.add(item_pedido)
        
        from ..models import get_brasilia_now
        pedido.status = 'finalizado' # Altera para finalizado após o retorno
        pedido.divida = float(divida) # Adiciona o campo divida
        pedido.total = pedido.calcular_total() # Recalcula o total com a dívida
        pedido.updated_at = get_brasilia_now()
        
        db.session.commit()
        return jsonify({
            'message': 'Pedido de retorno criado com sucesso',
            'pedido': pedido.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar pedido de retorno: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@pedidos_bp.route('/<int:pedido_id>/itens', methods=['GET'])
@token_required
def get_itens_pedido(pedido_id):
    """
    Obtém os itens de um pedido específico
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({'message': 'Pedido não encontrado'}), 404
        
        itens = []
        for item in pedido.itens:
            itens.append(item.to_dict())
        
        return jsonify({
            'pedido_id': pedido.id,
            'status': pedido.status,
            'total': float(pedido.total),
            'itens': itens
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter itens do pedido: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@pedidos_bp.route('/<int:pedido_id>/imprimir', methods=['GET'])
@token_required
def imprimir_pedido(pedido_id):
    """
    Gera uma nota fiscal (PDF) para o pedido de SAÍDA
    """
    try:
        # Importação condicional para evitar erros em sistemas sem GTK
        from weasyprint import HTML
        
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({'message': 'Pedido não encontrado'}), 404
        
        itens_html = ''.join([
            f'''
            <tr>
                <td>{item.produto.nome}</td>
                <td>{float(item.quantidade_saida):.3f}</td>
                <td>R$ {float(item.preco_unitario):.2f}</td>
                <td>R$ {float(item.quantidade_saida * item.preco_unitario):.2f}</td>
            </tr>
            '''
            for item in pedido.itens
        ])

        html_content = render_template(
            'nota_fiscal_saida.html', # Usando um template específico para Saída
            pedido=pedido,
            itens_html=itens_html
        )
        
        html = HTML(string=html_content)
        pdf = html.write_pdf()
        
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=nota_fiscal_saida_pedido_{pedido_id}.pdf'
        return response

    except Exception as e:
        current_app.logger.error(f"Erro ao gerar nota fiscal de saída: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@pedidos_bp.route('/<int:pedido_id>/imprimir_retorno', methods=['GET'])
@token_required
def imprimir_pedido_retorno(pedido_id):
    """
    Gera uma nota fiscal (PDF) para o pedido de RETORNO/FINALIZADO
    """
    try:
        # Importação condicional para evitar erros em sistemas sem GTK
        from weasyprint import HTML
        
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({'message': 'Pedido não encontrado'}), 404
        
        if pedido.status != 'finalizado':
            return jsonify({'message': 'Apenas pedidos finalizados podem ter nota de retorno'}), 400
        
        itens_html = ''.join([
            f'''
            <tr>
                <td>{item.produto.nome}</td>
                <td>{float(item.quantidade_saida):.3f}</td>
                <td>{float(item.quantidade_retorno):.3f}</td>
                <td>{float(item.quantidade_vendida()):.3f}</td>
                <td>R$ {float(item.preco_unitario):.2f}</td>
                <td>R$ {float(item.valor_total()):.2f}</td>
            </tr>
            '''
            for item in pedido.itens
        ])

        html_content = render_template(
            'nota_fiscal_retorno.html', # Usando um template específico para Retorno
            pedido=pedido,
            itens_html=itens_html
        )
        
        html = HTML(string=html_content)
        pdf = html.write_pdf()
        
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=nota_fiscal_retorno_pedido_{pedido_id}.pdf'
        return response

    except Exception as e:
        current_app.logger.error(f"Erro ao gerar nota fiscal de retorno: {e}")
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
        
        db.session.delete(pedido)
        db.session.commit()
        
        return jsonify({'message': 'Pedido removido com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao remover pedido: {e}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500
