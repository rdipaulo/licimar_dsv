"""
Rotas para relatórios personalizados
"""
from flask import Blueprint, request, jsonify, current_app, send_file
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from models import Pedido, ItemPedido, Produto, Ambulante, User
from database import db
from utils.decorators import admin_required, log_action
from utils.helpers import generate_report_filename
import io
import csv
import json

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/vendas', methods=['GET'])
@admin_required
def relatorio_vendas():
    """
    Relatório de vendas com filtros personalizados
    """
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        ambulante_id = request.args.get('ambulante_id', type=int)
        produto_id = request.args.get('produto_id', type=int)
        formato = request.args.get('formato', 'json')  # json, csv, pdf
        
        # Query base
        query = db.session.query(
            Pedido.id.label('pedido_id'),
            Pedido.data_operacao,
            Ambulante.nome.label('ambulante_nome'),
            Produto.nome.label('produto_nome'),
            ItemPedido.quantidade_saida,
            ItemPedido.quantidade_retorno,
            (ItemPedido.quantidade_saida - ItemPedido.quantidade_retorno).label('quantidade_vendida'),
            ItemPedido.preco_unitario,
            ((ItemPedido.quantidade_saida - ItemPedido.quantidade_retorno) * ItemPedido.preco_unitario).label('valor_total')
        ).join(
            Ambulante, Pedido.ambulante_id == Ambulante.id
        ).join(
            ItemPedido, Pedido.id == ItemPedido.pedido_id
        ).join(
            Produto, ItemPedido.produto_id == Produto.id
        )
        
        # Aplica filtros
        if data_inicio:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
                query = query.filter(Pedido.data_operacao >= data_inicio_dt)
            except ValueError:
                return jsonify({'message': 'Data de início inválida. Use formato YYYY-MM-DD'}), 400
        
        if data_fim:
            try:
                data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Pedido.data_operacao < data_fim_dt)
            except ValueError:
                return jsonify({'message': 'Data de fim inválida. Use formato YYYY-MM-DD'}), 400
        
        if ambulante_id:
            query = query.filter(Pedido.ambulante_id == ambulante_id)
        
        if produto_id:
            query = query.filter(ItemPedido.produto_id == produto_id)
        
        # Ordena por data
        query = query.order_by(Pedido.data_operacao.desc())
        
        # Executa a query
        resultados = query.all()
        
        # Calcula totais
        total_vendas = sum(float(r.valor_total) for r in resultados)
        total_itens = sum(float(r.quantidade_vendida) for r in resultados)
        
        # Formata os dados
        dados = []
        for r in resultados:
            dados.append({
                'pedido_id': r.pedido_id,
                'data_operacao': r.data_operacao.isoformat() if r.data_operacao else None,
                'ambulante_nome': r.ambulante_nome,
                'produto_nome': r.produto_nome,
                'quantidade_saida': float(r.quantidade_saida),
                'quantidade_retorno': float(r.quantidade_retorno),
                'quantidade_vendida': float(r.quantidade_vendida),
                'preco_unitario': float(r.preco_unitario),
                'valor_total': float(r.valor_total)
            })
        
        relatorio = {
            'filtros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'ambulante_id': ambulante_id,
                'produto_id': produto_id
            },
            'resumo': {
                'total_vendas': total_vendas,
                'total_itens': total_itens,
                'total_registros': len(dados)
            },
            'dados': dados
        }
        
        if formato == 'csv':
            return _export_csv(dados, 'relatorio_vendas')
        elif formato == 'json':
            return jsonify(relatorio), 200
        else:
            return jsonify({'message': 'Formato não suportado'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar relatório de vendas: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@relatorios_bp.route('/produtos-mais-vendidos', methods=['GET'])
@admin_required
def relatorio_produtos_mais_vendidos():
    """
    Relatório dos produtos mais vendidos
    """
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        limite = request.args.get('limite', 10, type=int)
        formato = request.args.get('formato', 'json')
        
        # Query base
        query = db.session.query(
            Produto.id,
            Produto.nome,
            func.sum(ItemPedido.quantidade_saida - ItemPedido.quantidade_retorno).label('total_vendido'),
            func.sum((ItemPedido.quantidade_saida - ItemPedido.quantidade_retorno) * ItemPedido.preco_unitario).label('total_faturamento'),
            func.count(ItemPedido.id).label('total_pedidos')
        ).join(
            ItemPedido, Produto.id == ItemPedido.produto_id
        ).join(
            Pedido, ItemPedido.pedido_id == Pedido.id
        )
        
        # Aplica filtros de data
        if data_inicio:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
                query = query.filter(Pedido.data_operacao >= data_inicio_dt)
            except ValueError:
                return jsonify({'message': 'Data de início inválida. Use formato YYYY-MM-DD'}), 400
        
        if data_fim:
            try:
                data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Pedido.data_operacao < data_fim_dt)
            except ValueError:
                return jsonify({'message': 'Data de fim inválida. Use formato YYYY-MM-DD'}), 400
        
        # Agrupa e ordena
        query = query.group_by(Produto.id, Produto.nome)
        query = query.order_by(func.sum(ItemPedido.quantidade_saida - ItemPedido.quantidade_retorno).desc())
        query = query.limit(limite)
        
        # Executa a query
        resultados = query.all()
        
        # Formata os dados
        dados = []
        for r in resultados:
            dados.append({
                'produto_id': r.id,
                'produto_nome': r.nome,
                'total_vendido': float(r.total_vendido or 0),
                'total_faturamento': float(r.total_faturamento or 0),
                'total_pedidos': r.total_pedidos
            })
        
        relatorio = {
            'filtros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'limite': limite
            },
            'dados': dados
        }
        
        if formato == 'csv':
            return _export_csv(dados, 'produtos_mais_vendidos')
        else:
            return jsonify(relatorio), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar relatório de produtos mais vendidos: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@relatorios_bp.route('/performance-ambulantes', methods=['GET'])
@admin_required
def relatorio_performance_ambulantes():
    """
    Relatório de performance dos ambulantes
    """
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        formato = request.args.get('formato', 'json')
        
        # Query base
        query = db.session.query(
            Ambulante.id,
            Ambulante.nome,
            func.count(Pedido.id).label('total_pedidos'),
            func.sum(Pedido.total).label('total_faturamento'),
            func.avg(Pedido.total).label('ticket_medio')
        ).outerjoin(
            Pedido, Ambulante.id == Pedido.ambulante_id
        )
        
        # Aplica filtros de data
        if data_inicio:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
                query = query.filter(or_(Pedido.data_operacao >= data_inicio_dt, Pedido.data_operacao.is_(None)))
            except ValueError:
                return jsonify({'message': 'Data de início inválida. Use formato YYYY-MM-DD'}), 400
        
        if data_fim:
            try:
                data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(or_(Pedido.data_operacao < data_fim_dt, Pedido.data_operacao.is_(None)))
            except ValueError:
                return jsonify({'message': 'Data de fim inválida. Use formato YYYY-MM-DD'}), 400
        
        # Agrupa e ordena
        query = query.group_by(Ambulante.id, Ambulante.nome)
        query = query.order_by(func.sum(Pedido.total).desc())
        
        # Executa a query
        resultados = query.all()
        
        # Formata os dados
        dados = []
        for r in resultados:
            dados.append({
                'ambulante_id': r.id,
                'ambulante_nome': r.nome,
                'total_pedidos': r.total_pedidos or 0,
                'total_faturamento': float(r.total_faturamento or 0),
                'ticket_medio': float(r.ticket_medio or 0)
            })
        
        relatorio = {
            'filtros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim
            },
            'dados': dados
        }
        
        if formato == 'csv':
            return _export_csv(dados, 'performance_ambulantes')
        else:
            return jsonify(relatorio), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar relatório de performance de ambulantes: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@relatorios_bp.route('/estoque', methods=['GET'])
@admin_required
def relatorio_estoque():
    """
    Relatório de estoque atual
    """
    try:
        formato = request.args.get('formato', 'json')
        estoque_baixo_only = request.args.get('estoque_baixo', type=bool)
        
        # Query base
        query = db.session.query(Produto)
        
        if estoque_baixo_only:
            query = query.filter(Produto.estoque <= Produto.estoque_minimo)
        
        query = query.filter(Produto.active == True)
        query = query.order_by(Produto.nome)
        
        # Executa a query
        produtos = query.all()
        
        # Formata os dados
        dados = []
        for produto in produtos:
            dados.append({
                'produto_id': produto.id,
                'produto_nome': produto.nome,
                'estoque_atual': produto.estoque,
                'estoque_minimo': produto.estoque_minimo,
                'categoria': produto.categoria_obj.nome if produto.categoria_obj else None,
                'preco': float(produto.preco),
                'estoque_baixo': produto.is_estoque_baixo(),
                'valor_estoque': float(produto.estoque * produto.preco)
            })
        
        # Calcula totais
        total_produtos = len(dados)
        produtos_estoque_baixo = sum(1 for d in dados if d['estoque_baixo'])
        valor_total_estoque = sum(d['valor_estoque'] for d in dados)
        
        relatorio = {
            'resumo': {
                'total_produtos': total_produtos,
                'produtos_estoque_baixo': produtos_estoque_baixo,
                'valor_total_estoque': valor_total_estoque
            },
            'dados': dados
        }
        
        if formato == 'csv':
            return _export_csv(dados, 'relatorio_estoque')
        else:
            return jsonify(relatorio), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar relatório de estoque: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@relatorios_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard_metrics():
    """
    Métricas para dashboard principal
    """
    try:
        # Período padrão: últimos 30 dias
        data_inicio = datetime.now() - timedelta(days=30)
        
        # Vendas do período
        vendas_periodo = db.session.query(
            func.sum((ItemPedido.quantidade_saida - ItemPedido.quantidade_retorno) * ItemPedido.preco_unitario)
        ).join(
            Pedido, ItemPedido.pedido_id == Pedido.id
        ).filter(
            Pedido.data_operacao >= data_inicio
        ).scalar() or 0
        
        # Vendas de hoje
        hoje = datetime.now().date()
        vendas_hoje = db.session.query(
            func.sum((ItemPedido.quantidade_saida - ItemPedido.quantidade_retorno) * ItemPedido.preco_unitario)
        ).join(
            Pedido, ItemPedido.pedido_id == Pedido.id
        ).filter(
            func.date(Pedido.data_operacao) == hoje
        ).scalar() or 0
        
        # Produtos com estoque baixo
        produtos_estoque_baixo = Produto.query.filter(
            Produto.estoque <= Produto.estoque_minimo,
            Produto.active == True
        ).count()
        
        # Total de ambulantes ativos
        ambulantes_ativos = Ambulante.query.filter_by(status='ativo').count()
        
        # Pedidos em aberto (status saída)
        pedidos_abertos = Pedido.query.filter_by(status='saida').count()
        
        # Produto mais vendido do período
        produto_mais_vendido = db.session.query(
            Produto.nome,
            func.sum(ItemPedido.quantidade_saida - ItemPedido.quantidade_retorno).label('total_vendido')
        ).join(
            ItemPedido, Produto.id == ItemPedido.produto_id
        ).join(
            Pedido, ItemPedido.pedido_id == Pedido.id
        ).filter(
            Pedido.data_operacao >= data_inicio
        ).group_by(
            Produto.id, Produto.nome
        ).order_by(
            func.sum(ItemPedido.quantidade_saida - ItemPedido.quantidade_retorno).desc()
        ).first()
        
        # Vendas por dia (últimos 7 dias)
        vendas_por_dia = []
        for i in range(7):
            data = datetime.now().date() - timedelta(days=i)
            vendas_dia = db.session.query(
                func.sum((ItemPedido.quantidade_saida - ItemPedido.quantidade_retorno) * ItemPedido.preco_unitario)
            ).join(
                Pedido, ItemPedido.pedido_id == Pedido.id
            ).filter(
                func.date(Pedido.data_operacao) == data
            ).scalar() or 0
            
            vendas_por_dia.append({
                'data': data.isoformat(),
                'vendas': float(vendas_dia)
            })
        
        vendas_por_dia.reverse()  # Ordem cronológica
        
        return jsonify({
            'vendas_periodo': float(vendas_periodo),
            'vendas_hoje': float(vendas_hoje),
            'produtos_estoque_baixo': produtos_estoque_baixo,
            'ambulantes_ativos': ambulantes_ativos,
            'pedidos_abertos': pedidos_abertos,
            'produto_mais_vendido': {
                'nome': produto_mais_vendido.nome if produto_mais_vendido else None,
                'quantidade': float(produto_mais_vendido.total_vendido) if produto_mais_vendido else 0
            },
            'vendas_por_dia': vendas_por_dia
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar métricas do dashboard: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

def _export_csv(dados, nome_arquivo):
    """
    Exporta dados para CSV
    """
    try:
        if not dados:
            return jsonify({'message': 'Nenhum dado para exportar'}), 400
        
        # Cria arquivo CSV em memória
        output = io.StringIO()
        
        # Pega as chaves do primeiro item como cabeçalhos
        fieldnames = dados[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        # Escreve cabeçalho e dados
        writer.writeheader()
        writer.writerows(dados)
        
        # Prepara resposta
        output.seek(0)
        filename = generate_report_filename(nome_arquivo, 'csv')
        
        # Cria arquivo temporário
        csv_content = output.getvalue()
        output.close()
        
        # Retorna arquivo
        return current_app.response_class(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        current_app.logger.error(f"Erro ao exportar CSV: {e}")
        return jsonify({'message': 'Erro ao exportar CSV'}), 500
