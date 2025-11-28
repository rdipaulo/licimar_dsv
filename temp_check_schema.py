from sqlalchemy import inspect, create_engine

db_path = r'c:\licimar_dsv\backend\licimar_mvp_app\instance\licimar_dev.db'
engine = create_engine(f'sqlite:///{db_path}')

inspector = inspect(engine)
columns = inspector.get_columns('produtos')
print('Colunas da tabela produtos:')
for col in columns:
    print(f"  {col['name']}: {col['type']}")

