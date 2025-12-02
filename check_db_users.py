#!/usr/bin/env python3
"""Verificar usuários no banco de dados SQLite"""
import sqlite3
import os

db_path = "backend/licimar_mvp_app/instance/licimar_dev.db"

if not os.path.exists(db_path):
    print(f"❌ Banco de dados não encontrado: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Listar usuários
cursor.execute("SELECT id, username, email, active FROM users;")
users = cursor.fetchall()

print(f"\n✓ Total de usuários no banco: {len(users)}\n")

if users:
    for user_id, username, email, active in users:
        active_str = "✓ Ativo" if active else "✗ Inativo"
        print(f"  ID: {user_id}")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Status: {active_str}")
        print()
else:
    print("❌ Nenhum usuário encontrado no banco de dados")

conn.close()
