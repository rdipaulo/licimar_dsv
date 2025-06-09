from src.database import db
from datetime import datetime

class Log(db.Model):
    __tablename__ = "logs"
    
    id = db.Column(db.Integer, primary_key=True)
    # Chave estrangeira para User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Pode ser nulo para ações do sistema?
    action = db.Column(db.String(50), nullable=False) # Ex: CREATE, UPDATE, DELETE, LOGIN
    entity_type = db.Column(db.String(50), nullable=True) # Ex: User, Produto, Pedido
    entity_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True) # Detalhes em JSON
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Log {self.id} - User {self.user_id} - Action {self.action}>'
    