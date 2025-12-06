"""
Modelos de banco de dados para o sistema Licimar
"""
from datetime import datetime
import pytz
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from .database import db

# Timezone de Brasília
TZ_BRASILIA = pytz.timezone('America/Sao_Paulo')

def get_brasilia_now():
    """Retorna data/hora atual em Brasília"""
    return datetime.now(TZ_BRASILIA).replace(tzinfo=None)

class User(db.Model):
    """Modelo para usuários do sistema"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='operador', nullable=False)  # 'admin' ou 'operador'
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=get_brasilia_now)
    updated_at = db.Column(db.DateTime, default=get_brasilia_now, onupdate=get_brasilia_now)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.role == 'admin'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Cliente(db.Model):
    """Modelo para clientes/vendedores"""
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    telefone = db.Column(db.String(20))
    cpf = db.Column(db.String(14), unique=True)
    endereco = db.Column(db.Text)
    status = db.Column(db.String(20), default='ativo', nullable=False)  # 'ativo' ou 'inativo'
    divida_acumulada = db.Column(db.Numeric(10, 2), default=0)  # Dívida acumulada do cliente
    created_at = db.Column(db.DateTime, default=get_brasilia_now)
    updated_at = db.Column(db.DateTime, default=get_brasilia_now, onupdate=get_brasilia_now)
    
    # Relacionamentos
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)
    
    @property
    def divida_pendente_total(self):
        """
        Calcula o saldo devedor total do cliente.
        
        Lógica:
        - Soma de todos os valor_divida (débitos) com status 'Em Aberto' ou 'Parcialmente Pago'
        - MENOS a soma de todos os cobranca_divida (abatimentos)
        
        Returns:
            float: Saldo devedor total
        """
        from sqlalchemy import func, or_
        
        # Obter todas as dívidas do cliente que não estão quitadas
        dividas_abertas = Divida.query.filter(
            Divida.id_cliente == self.id,
            or_(
                Divida.status == 'Em Aberto',
                Divida.status == 'Parcialmente Pago'
            )
        ).all()
        
        # Calcular total de débitos
        total_debitos = sum(float(d.valor_divida) for d in dividas_abertas)
        
        # Calcular total de abatimentos (pagamentos de dívida)
        total_abatimentos = db.session.query(
            func.sum(PagamentoDivida.cobranca_divida)
        ).filter(
            PagamentoDivida.id_divida.in_(
                [d.id_divida for d in dividas_abertas]
            )
        ).scalar() or 0
        
        # Retornar saldo devedor
        saldo_devedor = float(total_debitos) - float(total_abatimentos)
        return max(0, saldo_devedor)  # Nunca retorna negativo
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'cpf': self.cpf,
            'endereco': self.endereco,
            'status': self.status,
            'divida_acumulada': float(self.divida_acumulada) if self.divida_acumulada else 0,
            'divida_pendente_total': self.divida_pendente_total,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Alias para compatibilidade com código legado
Ambulante = Cliente

class Categoria(db.Model):
    """Modelo para categorias de produtos"""
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=get_brasilia_now)
    updated_at = db.Column(db.DateTime, default=get_brasilia_now, onupdate=get_brasilia_now)
    
    # Relacionamentos
    produtos = db.relationship('Produto', backref='categoria_obj', lazy=True)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Produto(db.Model):
    """Modelo para produtos"""
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    estoque = db.Column(db.Integer, default=0, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    imagem_url = db.Column(db.String(255))
    descricao = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, nullable=False)
    estoque_minimo = db.Column(db.Integer, default=10)  # Para alertas de estoque baixo
    nao_devolve = db.Column(db.Boolean, default=False, nullable=False) # Se o produto não pode ser devolvido (ex: Gelo Seco)
    peso = db.Column(db.Numeric(5, 2), default=0) # Peso em kg para produtos como gelo seco (1.5, 1.7, etc)
    created_at = db.Column(db.DateTime, default=get_brasilia_now)
    updated_at = db.Column(db.DateTime, default=get_brasilia_now, onupdate=get_brasilia_now)
    
    # Relacionamentos
    itens_pedido = db.relationship('ItemPedido', backref='produto', lazy=True)
    
    def is_estoque_baixo(self):
        """Verifica se o estoque está baixo"""
        return self.estoque <= self.estoque_minimo
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'preco': float(self.preco),
            'estoque': self.estoque,
            'categoria_id': self.categoria_id,
            'categoria_nome': self.categoria_obj.nome if self.categoria_obj else None,
            'imagem_url': self.imagem_url,
            'descricao': self.descricao,
            'active': self.active,
            'estoque_minimo': self.estoque_minimo,
            'estoque_baixo': self.is_estoque_baixo(),
            'nao_devolve': self.nao_devolve,
            'peso': float(self.peso) if self.peso else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class RegraCobranca(db.Model):
    """Modelo para regras de cobrança de dívida"""
    __tablename__ = 'regras_cobranca'
    
    id = db.Column(db.Integer, primary_key=True)
    faixa_inicial = db.Column(db.Numeric(10, 2), nullable=False)
    faixa_final = db.Column(db.Numeric(10, 2), nullable=False)
    percentual = db.Column(db.Numeric(5, 2), nullable=False)  # Percentual de desconto/cobrança
    descricao = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=get_brasilia_now)
    updated_at = db.Column(db.DateTime, default=get_brasilia_now, onupdate=get_brasilia_now)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'faixa_inicial': float(self.faixa_inicial),
            'faixa_final': float(self.faixa_final),
            'percentual': float(self.percentual),
            'descricao': self.descricao,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Pedido(db.Model):
    """Modelo para pedidos"""
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    data_operacao = db.Column(db.DateTime, default=get_brasilia_now)
    status = db.Column(db.String(20), default='saida', nullable=False)  # 'saida', 'retorno', 'finalizado'
    total = db.Column(db.Numeric(10, 2), default=0)
    divida = db.Column(db.Numeric(10, 2), default=0) # Novo campo para dívida
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_brasilia_now)
    updated_at = db.Column(db.DateTime, default=get_brasilia_now, onupdate=get_brasilia_now)
    
    # Relacionamentos
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True, cascade='all, delete-orphan')
    
    def calcular_total(self):
        """Calcula o total do pedido baseado nos itens e adiciona a dívida"""
        total_itens = 0.0
        for item in self.itens:
            quantidade_vendida = float(item.quantidade_saida) - float(item.quantidade_retorno)
            total_itens += float(quantidade_vendida * float(item.preco_unitario))
        
        total_final = float(total_itens) + float(self.divida or 0)
        self.total = total_final
        return total_final
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'cliente_nome': self.cliente.nome if self.cliente else None,
            # Aliases para compatibilidade com código legado
            'ambulante_id': self.cliente_id,
            'ambulante_nome': self.cliente.nome if self.cliente else None,
            'data_operacao': self.data_operacao.isoformat() if self.data_operacao else None,
            'status': self.status,
            'total': float(self.total),
            'divida': float(self.divida),
            'observacoes': self.observacoes,
            'itens': [item.to_dict() for item in self.itens],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ItemPedido(db.Model):
    """Modelo para itens de pedido"""
    __tablename__ = 'itens_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade_saida = db.Column(db.Numeric(10, 3), nullable=False, default=0)  # NUMERIC para suportar decimais (ex: 2.500 kg)
    quantidade_retorno = db.Column(db.Integer, nullable=False, default=0)  # INT para quantidade
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=get_brasilia_now)
    
    def quantidade_vendida(self):
        """Calcula a quantidade vendida (saída - retorno)"""
        return self.quantidade_saida - self.quantidade_retorno
    
    def valor_total(self):
        """Calcula o valor total do item"""
        return self.quantidade_vendida() * self.preco_unitario
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'produto_id': self.produto_id,
            'produto_nome': self.produto.nome if self.produto else None,
            'quantidade_saida': float(self.quantidade_saida),
            'quantidade_retorno': int(self.quantidade_retorno),
            'quantidade_vendida': int(self.quantidade_vendida()),
            'preco_unitario': float(self.preco_unitario),
            'valor_total': float(self.valor_total()),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Divida(db.Model):
    """Modelo para registro de dívidas de clientes"""
    __tablename__ = 'dividas'
    
    id_divida = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    data_registro = db.Column(db.DateTime, default=get_brasilia_now, nullable=False)
    valor_divida = db.Column(db.Numeric(10, 2), nullable=False)  # Valor total do débito
    descricao = db.Column(db.String(255))
    status = db.Column(db.String(50), default='Em Aberto', nullable=False)  # 'Em Aberto', 'Parcialmente Pago', 'Quitado'
    created_at = db.Column(db.DateTime, default=get_brasilia_now)
    updated_at = db.Column(db.DateTime, default=get_brasilia_now, onupdate=get_brasilia_now)
    
    # Relacionamentos
    cliente = db.relationship('Cliente', backref='dividas', foreign_keys=[id_cliente])
    pagamentos = db.relationship('PagamentoDivida', backref='divida', lazy=True, cascade='all, delete-orphan')
    
    def calcular_saldo_devedor(self):
        """Calcula o saldo devedor (valor original - abatimentos)"""
        total_abatido = sum(float(p.cobranca_divida) for p in self.pagamentos)
        return float(self.valor_divida) - total_abatido
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id_divida': self.id_divida,
            'id_cliente': self.id_cliente,
            'cliente_nome': self.cliente.nome if self.cliente else None,
            'data_registro': self.data_registro.isoformat() if self.data_registro else None,
            'valor_divida': float(self.valor_divida),
            'descricao': self.descricao,
            'status': self.status,
            'saldo_devedor': self.calcular_saldo_devedor(),
            'total_abatido': sum(float(p.cobranca_divida) for p in self.pagamentos),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PagamentoDivida(db.Model):
    """Modelo para registrar pagamentos/abatimentos de dívidas"""
    __tablename__ = 'pagamentos_divida'
    
    id_lancamento = db.Column(db.Integer, primary_key=True)
    id_divida = db.Column(db.Integer, db.ForeignKey('dividas.id_divida'), nullable=False)
    data_pagamento = db.Column(db.DateTime, default=get_brasilia_now, nullable=False)
    cobranca_divida = db.Column(db.Numeric(10, 2), nullable=False)  # Valor cobrado (sempre positivo)
    id_nota_venda = db.Column(db.Integer)  # Referência ao pedido/nota onde foi cobrado
    descricao = db.Column(db.String(255))  # Motivo do abatimento
    created_at = db.Column(db.DateTime, default=get_brasilia_now)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id_lancamento': self.id_lancamento,
            'id_divida': self.id_divida,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'cobranca_divida': float(self.cobranca_divida),
            'id_nota_venda': self.id_nota_venda,
            'descricao': self.descricao,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PedidoConsignacao(db.Model):
    """Modelo para pedidos de consignação (cabeçalho)"""
    __tablename__ = 'pedidos_consignacao'
    
    id_pedido = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    data_pedido = db.Column(db.DateTime, default=get_brasilia_now, nullable=False)
    tipo_operacao = db.Column(db.String(50), nullable=False)  # 'RETIRADA', 'DEVOLUCAO', 'ACERTO'
    valor_total_final = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(50), default='Aberto', nullable=False)  # 'Aberto', 'Fechado', 'Cancelado'
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_brasilia_now)
    updated_at = db.Column(db.DateTime, default=get_brasilia_now, onupdate=get_brasilia_now)
    
    # Relacionamentos
    cliente = db.relationship('Cliente', backref='pedidos_consignacao', foreign_keys=[id_cliente])
    itens = db.relationship('ItemPedidoConsignacao', backref='pedido_consignacao', lazy=True, cascade='all, delete-orphan')
    
    def calcular_total(self):
        """Calcula o total do pedido baseado nos itens"""
        total = sum(float(item.subtotal) for item in self.itens)
        self.valor_total_final = total
        return total
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id_pedido': self.id_pedido,
            'id_cliente': self.id_cliente,
            'cliente_nome': self.cliente.nome if self.cliente else None,
            'data_pedido': self.data_pedido.isoformat() if self.data_pedido else None,
            'tipo_operacao': self.tipo_operacao,
            'valor_total_final': float(self.valor_total_final),
            'status': self.status,
            'observacoes': self.observacoes,
            'itens': [item.to_dict() for item in self.itens],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ItemPedidoConsignacao(db.Model):
    """Modelo para itens de pedido de consignação (detalhes)"""
    __tablename__ = 'itens_pedido_consignacao'
    
    id_item_pedido = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos_consignacao.id_pedido'), nullable=False)
    id_produto = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade_negociada = db.Column(db.Numeric(10, 2), nullable=False)
    valor_unitario_venda = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=get_brasilia_now)
    
    # Relacionamentos
    produto = db.relationship('Produto', backref='itens_consignacao', foreign_keys=[id_produto])
    
    def calcular_subtotal(self):
        """Calcula o subtotal do item"""
        self.subtotal = float(self.quantidade_negociada) * float(self.valor_unitario_venda)
        return self.subtotal
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id_item_pedido': self.id_item_pedido,
            'id_pedido': self.id_pedido,
            'id_produto': self.id_produto,
            'produto_nome': self.produto.nome if self.produto else None,
            'quantidade_negociada': float(self.quantidade_negociada),
            'valor_unitario_venda': float(self.valor_unitario_venda),
            'subtotal': float(self.subtotal),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Log(db.Model):
    """Modelo para logs do sistema"""
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))  # IPv6 pode ter até 45 caracteres
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_brasilia_now)
    
    # Relacionamento
    user = db.relationship('User', backref='logs')
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
