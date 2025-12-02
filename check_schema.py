#!/usr/bin/env python3
"""Verificar schema da tabela pedidos"""
import sqlite3

db_path = "backend/licimar_mvp_app/instance/licimar_dev.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar colunas da tabela pedidos
cursor.execute("PRAGMA table_info(pedidos)")
columns = cursor.fetchall()

print(f"\n✓ Colunas da tabela 'pedidos':\n")
for col_id, col_name, col_type, not_null, default, pk in columns:
    nullable = "NOT NULL" if not_null else "NULL"
    print(f"  {col_name:20s} | {col_type:15s} | {nullable}")

# Procura por coluna divida
cursor.execute("PRAGMA table_info(pedidos)")
columns = [row[1] for row in cursor.fetchall()]

if 'divida' not in columns:
    print(f"\n⚠ Campo 'divida' não existe na tabela!")
else:
    print(f"\n✓ Campo 'divida' existe na tabela!")

conn.close()
