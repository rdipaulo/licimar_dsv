"""
Rotas para gerenciamento de pedidos
"""
from flask import Blueprint, request, jsonify, current_app, render_template, make_response, send_file
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
        
        # DEBUG
        current_app.logger.info(f"[DEBUG] Dados recebidos: {data}")
        
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
        
        # DEBUG
        current_app.logger.info(f"[DEBUG] Pedido atualizado - divida: {pedido.divida}, total: {pedido.total}")
        
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
        from fpdf import FPDF
        from io import BytesIO
        
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({'message': 'Pedido não encontrado'}), 404
        
        # Criar PDF com fpdf2
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(0, 10, f'NOTA FISCAL DE SAIDA - Pedido #{pedido.id}', ln=True, align='C')
        
        pdf.set_font('Helvetica', '', 10)
        pdf.ln(10)
        
        # Informações do cliente
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 5, f'Cliente: {pedido.cliente.nome}', ln=True)
        pdf.cell(0, 5, f'Data: {pedido.created_at.strftime("%d/%m/%Y %H:%M")}', ln=True)
        pdf.cell(0, 5, f'Total: R$ {float(pedido.total):.2f}', ln=True)
        pdf.ln(5)
        
        # Tabela de itens
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(60, 8, 'Produto', border=1)
        pdf.cell(30, 8, 'Qtd', border=1, align='C')
        pdf.cell(30, 8, 'Preco Unit.', border=1, align='C')
        pdf.cell(30, 8, 'Total Item', border=1, align='C')
        pdf.ln()
        
        pdf.set_font('Helvetica', '', 9)
        for item in pedido.itens:
            quantidade = float(item.quantidade_saida)
            preco = float(item.preco_unitario)
            total = quantidade * preco
            
            pdf.cell(60, 8, item.produto.nome[:30], border=1)
            pdf.cell(30, 8, f'{quantidade:.3f}', border=1, align='C')
            pdf.cell(30, 8, f'{preco:.2f}', border=1, align='C')
            pdf.cell(30, 8, f'{total:.2f}', border=1, align='C')
            pdf.ln()
        
        # Rodapé
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 8, f'TOTAL: R$ {float(pedido.total):.2f}', align='R')
        pdf.ln()
        
        # Adicionar Dívida Pendente
        saldo_devedor = pedido.cliente.divida_pendente_total
        if saldo_devedor > 0:
            pdf.set_font('Helvetica', '', 10)
            pdf.cell(0, 8, f'ATENÇÃO - Dívida Pendente: R$ {saldo_devedor:.2f}', align='R')
        
        # Retornar PDF como bytes usando BytesIO
        pdf_bytes = pdf.output()
        pdf_io = BytesIO(pdf_bytes)
        pdf_io.seek(0)
        
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'nota_fiscal_saida_{pedido_id}.pdf'
        )

    except Exception as e:
        current_app.logger.error(f"Erro ao gerar nota fiscal de saída: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@pedidos_bp.route('/<int:pedido_id>/imprimir_retorno', methods=['GET'])
@token_required
def imprimir_pedido_retorno(pedido_id):
    """
    Gera uma nota fiscal (PDF) para o pedido de RETORNO/FINALIZADO
    """
    try:
        from fpdf import FPDF
        from io import BytesIO
        
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({'message': 'Pedido não encontrado'}), 404
        
        if pedido.status != 'finalizado':
            return jsonify({'message': 'Apenas pedidos finalizados podem ter nota de retorno'}), 400
        
        # Criar PDF com fpdf2
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(0, 10, f'NOTA FISCAL DE RETORNO - Pedido #{pedido.id}', ln=True, align='C')
        
        pdf.set_font('Helvetica', '', 10)
        pdf.ln(10)
        
        # Informações do cliente
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 5, f'Cliente: {pedido.cliente.nome}', ln=True)
        pdf.cell(0, 5, f'Data: {pedido.created_at.strftime("%d/%m/%Y %H:%M")}', ln=True)
        pdf.ln(5)
        
        # Tabela de itens
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(40, 8, 'Produto', border=1)
        pdf.cell(20, 8, 'Saida', border=1, align='C')
        pdf.cell(20, 8, 'Retorno', border=1, align='C')
        pdf.cell(20, 8, 'Vendido', border=1, align='C')
        pdf.cell(25, 8, 'Preco', border=1, align='C')
        pdf.cell(25, 8, 'Total', border=1, align='C')
        pdf.ln()
        
        pdf.set_font('Helvetica', '', 8)
        for item in pedido.itens:
            saida = float(item.quantidade_saida)
            retorno = float(item.quantidade_retorno)
            vendido = float(item.quantidade_vendida())
            preco = float(item.preco_unitario)
            total = float(item.valor_total())
            
            pdf.cell(40, 8, item.produto.nome[:20], border=1)
            pdf.cell(20, 8, f'{saida:.2f}', border=1, align='C')
            pdf.cell(20, 8, f'{retorno:.2f}', border=1, align='C')
            pdf.cell(20, 8, f'{vendido:.2f}', border=1, align='C')
            pdf.cell(25, 8, f'{preco:.2f}', border=1, align='C')
            pdf.cell(25, 8, f'{total:.2f}', border=1, align='C')
            pdf.ln()
        
        # Rodapé
        pdf.ln(5)
        pdf.set_font('Helvetica', '', 10)
        
        # Calcular subtotal (sem a cobrança de dívida)
        subtotal = float(pedido.total) - float(pedido.divida)
        
        pdf.cell(0, 8, f'Subtotal: R$ {subtotal:.2f}', align='R')
        pdf.ln()
        pdf.cell(0, 8, f'Cobrança de Dívida: R$ {float(pedido.divida):.2f}', align='R')
        pdf.ln()
        
        # Adicionar Dívida Pendente
        saldo_devedor = pedido.cliente.divida_pendente_total
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 8, f'Dívida Pendente: R$ {saldo_devedor:.2f}', align='R')
        pdf.ln()
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 8, f'TOTAL: R$ {float(pedido.total):.2f}', align='R')
        
        # Retornar PDF usando BytesIO
        pdf_bytes = pdf.output()
        pdf_io = BytesIO(pdf_bytes)
        pdf_io.seek(0)
        
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'nota_fiscal_retorno_{pedido_id}.pdf'
        )

    except Exception as e:
        current_app.logger.error(f"Erro ao gerar nota fiscal de retorno: {e}")
        import traceback
        traceback.print_exc()
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
