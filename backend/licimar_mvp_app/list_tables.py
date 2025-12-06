#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('instance/licimar_dev.db')
cursor = conn.cursor()

# Listar tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print('📊 TABELAS NO BANCO DE DADOS')
print('=' * 60)
print(f'Total de tabelas: {len(tables)}\n')

for table in tables:
    table_name = table[0]
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    print(f'✓ {table_name} ({len(columns)} colunas)')
    for col in columns:
        col_id, col_name, col_type, notnull, default, pk = col
        pk_str = ' [PK]' if pk else ''
        print(f'  ├─ {col_name}: {col_type}{pk_str}')
    print()

conn.close()
