#!/usr/bin/env python3
"""Verificar gelo no banco de dados"""
import sqlite3

db_path = "backend/licimar_mvp_app/instance/licimar_dev.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Buscar produto gelo
cursor.execute("""
    SELECT id, nome, categoria_id, preco, estoque, peso
    FROM produtos
    WHERE LOWER(nome) LIKE '%gelo%'
    ORDER BY nome
""")

geloS = cursor.fetchall()

print(f"\n✓ Produtos com 'gelo':\n")

if geloS:
    for id, nome, cat, preco, estoque, peso in geloS:
        print(f"  ID: {id}")
        print(f"  Nome: {nome}")
        print(f"  Categoria: {cat}")
        print(f"  Preço: R$ {preco}")
        print(f"  Estoque: {estoque}")
        print(f"  Peso: {peso}")
        print()
else:
    print("  ❌ Nenhum produto com 'gelo' encontrado")

conn.close()
