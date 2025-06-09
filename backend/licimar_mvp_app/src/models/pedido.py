from src.database import db
from datetime import datetime

class Pedido(db.Model):
    __tablename__ = "pedidos"
    
    id = db.Column(db.Integer, primary_key=True)
    # Chave estrangeira para Vendedor
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedores.id'), nullable=False)
    data_operacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default='EM_ABERTO') # Ex: EM_ABERTO, SAIDA, RETORNO, FECHADO
    valor_total_a_pagar = db.Column(db.Numeric(10, 2), nullable=True) # Calculado ao fechar
    # Chave estrangeira para User (quem criou o pedido)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Pode ser nulo se criado automaticamente?
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relacionamento com Itens de Pedido (um pedido tem vários itens)
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Pedido {self.id} - Vendedor {self.vendedor_id}>'
