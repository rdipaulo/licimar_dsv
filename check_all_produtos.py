#!/usr/bin/env python3
"""Verificar todos os produtos no banco"""
import sqlite3

db_path = "backend/licimar_mvp_app/instance/licimar_dev.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, nome, categoria_id, preco, estoque, active
    FROM produtos
    ORDER BY id
""")

produtos = cursor.fetchall()

print(f"\n✓ Total de produtos: {len(produtos)}\n")

for id, nome, cat, preco, estoque, active in produtos:
    ativo = "✓" if active else "✗"
    print(f"{id:3d} | {ativo} | {nome:30s} | R$ {preco:7.2f} | Estoque: {estoque:3d}")

conn.close()
