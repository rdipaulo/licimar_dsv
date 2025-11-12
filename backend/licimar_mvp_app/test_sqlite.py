import sqlite3
import os

# Caminho para o diretório da instância
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')

# Garante que o diretório da instância exista
print(f'Criando diretório da instância em: {instance_path}')
os.makedirs(instance_path, exist_ok=True)

# Caminho para o arquivo do banco de dados
db_path = os.path.join(instance_path, 'test.db')
print(f'Caminho do banco de dados: {db_path}')

conn = None
try:
    # Conecta ao banco de dados (o arquivo será criado se não existir)
    conn = sqlite3.connect(db_path)
    print(f'Conexão com o banco de dados {db_path} bem-sucedida.')
    
    cursor = conn.cursor()
    
    # Cria uma tabela de teste
    print('Criando tabela de teste...')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    
    # Insere um dado de teste
    print('Inserindo dados de teste...')
    cursor.execute('INSERT INTO test_table (name) VALUES (?)', ('teste',))
    
    # Salva (commit) as mudanças
    conn.commit()
    print('Dados inseridos com sucesso.')
    
    # Verifica se o dado foi inserido
    cursor.execute('SELECT * FROM test_table')
    row = cursor.fetchone()
    print(f'Dado lido do banco de dados: {row}')
    
except sqlite3.Error as e:
    print(f'Ocorreu um erro no SQLite: {e}')
finally:
    # Fecha a conexão
    if conn:
        conn.close()
        print('Conexão com o banco de dados fechada.')
