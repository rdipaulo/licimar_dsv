#!/usr/bin/env python
"""Teste de senha"""
import sys
sys.path.insert(0, 'C:\\licimar_dsv\\backend\\licimar_mvp_app')

import os
os.chdir('C:\\licimar_dsv\\backend\\licimar_mvp_app')

from src.database import db
from src.main import create_app
from src.models import User

app = create_app()

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        print("❌ Usuário admin não encontrado!")
    else:
        print(f"✅ Usuário encontrado: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Active: {admin.active}")
        print(f"Password Hash: {admin.password_hash[:50]}...")
        
        # Testar senha
        password_to_test = 'admin123'
        is_valid = admin.check_password(password_to_test)
        
        print(f"\nTestando senha '{password_to_test}':")
        print(f"Resultado: {is_valid}")
        
        if not is_valid:
            print("\n⚠️  Senha incorreta! Redefinindo...")
            admin.set_password('admin123')
            db.session.commit()
            print("✅ Senha redefinida para 'admin123'")
            
            # Testar novamente
            is_valid = admin.check_password('admin123')
            print(f"Teste após reset: {is_valid}")
