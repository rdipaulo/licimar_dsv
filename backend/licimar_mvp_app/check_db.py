#!/usr/bin/env python3
from src.database import db
from src.main import create_app

app = create_app()
with app.app_context():
    # Verificar tabelas
    inspector = db.inspect(db.engine)
    tabelas = inspector.get_table_names()
    print('Tabelas no banco:')
    for t in tabelas:
        print(f'  - {t}')
    
    # Contar registros
    print()
    from src.models import Pedido
    count = Pedido.query.count()
    print(f'Pedidos em Pedido.query: {count}')
    
    # Verificar SQL direto
    from sqlalchemy import text
    result = db.session.execute(text("SELECT count(*) FROM pedidos"))
    count_sql = result.scalar()
    print(f'Pedidos via SQL: {count_sql}')
