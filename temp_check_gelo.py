from sqlalchemy import create_engine, text

db_path = r'c:\licimar_dsv\backend\licimar_mvp_app\instance\licimar_dev.db'
engine = create_engine(f'sqlite:///{db_path}')

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, nome, preco, peso FROM produtos WHERE nome LIKE '%gelo%' OR nome LIKE '%Gelo%'"))
    print('Produtos Gelo:')
    rows = result.fetchall()
    if rows:
        for row in rows:
            print(f"  ID: {row[0]}, Nome: {row[1]}, Preco: R${row[2]:.2f}, Peso: {row[3]}")
    else:
        print("  Nenhum produto com 'gelo' no nome encontrado")
