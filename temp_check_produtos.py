from sqlalchemy import inspect, create_engine, text

db_path = r'c:\licimar_dsv\backend\licimar_mvp_app\instance\licimar_dev.db'
engine = create_engine(f'sqlite:///{db_path}')

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, nome, preco, peso FROM produtos LIMIT 5"))
    print('Produtos no banco:')
    for row in result:
        print(f"  ID: {row[0]}, Nome: {row[1]}, Preco: R${row[2]:.2f}, Peso: {row[3]}")
