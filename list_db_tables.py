#!/usr/bin/env python3
"""Listar todas as tabelas do banco de dados"""
import sqlite3
import os

db_path = "backend/licimar_mvp_app/instance/licimar_dev.db"

if not os.path.exists(db_path):
    print(f"❌ Banco de dados não encontrado: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Listar todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print(f"\n✓ Total de tabelas: {len(tables)}\n")

for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    print(f"  • {table_name}: {count} registros")

print()
conn.close()
