#!/usr/bin/env python3
"""Verificar e remover produtos duplicados"""
import sqlite3
import os

db_path = "backend/licimar_mvp_app/instance/licimar_dev.db"

if not os.path.exists(db_path):
    print(f"❌ Banco de dados não encontrado: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Buscar duplicados (mesmo nome + categoria)
cursor.execute("""
    SELECT nome, categoria_id, COUNT(*) as count, GROUP_CONCAT(id) as ids
    FROM produtos
    GROUP BY LOWER(nome), categoria_id
    HAVING count > 1
""")

duplicates = cursor.fetchall()

print(f"\n✓ Verificando duplicados (nome + categoria)...\n")

if duplicates:
    print(f"⚠ ENCONTRADOS {len(duplicates)} produtos duplicados:\n")
    for nome, cat_id, count, ids in duplicates:
        ids_list = ids.split(',')
        print(f"  Nome: {nome} | Categoria ID: {cat_id} | Duplicatas: {count}")
        print(f"  IDs: {ids}")
        print(f"  → Mantendo ID {ids_list[0]}, removendo {', '.join(ids_list[1:])}\n")
        
        # Remover duplicatas (manter a primeira)
        for id_to_remove in ids_list[1:]:
            cursor.execute("DELETE FROM produtos WHERE id = ?", (id_to_remove,))
            print(f"    ✓ Removido produto ID {id_to_remove}")
else:
    print("✓ Nenhum produto duplicado encontrado!")

conn.commit()
conn.close()

print("\n✓ Processo concluído!")
