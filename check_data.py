from sqlalchemy import create_engine, text
import os

db_path = os.path.join('instance', 'licimar_dev.db')
engine = create_engine(f'sqlite:///{db_path}')

with engine.connect() as conn:
    # Check ambulantes
    result = conn.execute(text("SELECT COUNT(*) FROM ambulantes"))
    amb_count = result.scalar()
    print(f"Ambulantes: {amb_count}")
    
    # Check produtos
    result = conn.execute(text("SELECT COUNT(*) FROM produtos"))
    prod_count = result.scalar()
    print(f"Produtos: {prod_count}")
    
    # Check categorias
    result = conn.execute(text("SELECT COUNT(*) FROM categorias"))
    cat_count = result.scalar()
    print(f"Categorias: {cat_count}")
    
    # List ambulantes
    if amb_count > 0:
        result = conn.execute(text("SELECT id, nome FROM ambulantes LIMIT 3"))
        print("\nAmbulantes:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")
    
    # List categorias
    if cat_count > 0:
        result = conn.execute(text("SELECT id, nome FROM categorias LIMIT 3"))
        print("\nCategorias:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")
    
    # List produtos
    if prod_count > 0:
        result = conn.execute(text("SELECT id, nome FROM produtos LIMIT 3"))
        print("\nProdutos:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")
