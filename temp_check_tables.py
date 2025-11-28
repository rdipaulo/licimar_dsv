from sqlalchemy import inspect, create_engine
import os

db_path = r'c:\licimar_dsv\backend\licimar_mvp_app\instance\licimar_dev.db'
engine = create_engine(f'sqlite:///{db_path}')

inspector = inspect(engine)
tables = inspector.get_table_names()
print('Tabelas no banco de dados:')
for table in tables:
    print(f"  {table}")
