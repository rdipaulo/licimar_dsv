from sqlalchemy import create_engine, text

db_path = r'c:\licimar_dsv\backend\licimar_mvp_app\instance\licimar_dev.db'
engine = create_engine(f'sqlite:///{db_path}')

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, username, email FROM users"))
    print('Usuários no banco:')
    for row in result:
        print(f"  ID: {row[0]}, Username: {row[1]}, Email: {row[2]}")
