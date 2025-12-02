#!/usr/bin/env python3
"""Verificar usuários no banco de dados"""
import sys
sys.path.insert(0, 'backend/licimar_mvp_app')

from src.database import db
from src import create_app
from src.models import User

app = create_app('development')

with app.app_context():
    users = User.query.all()
    print(f"\nTotal de usuários: {len(users)}\n")
    for u in users:
        print(f"ID: {u.id}, Username: {u.username}, Email: {u.email}, Active: {u.active}")
    print()
