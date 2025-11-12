#!/usr/bin/env python3
"""
Script de teste para debug do login
"""
import json
from src.main import create_app
from src.database import db
from src.models import User

# Criar app
app = create_app()

# Context para acesso ao banco
with app.app_context():
    # Verificar usuários
    users = User.query.all()
    print(f"\n✓ Total de usuários: {len(users)}")
    for user in users:
        print(f"  - {user.username} ({user.email})")
    
    # Testar login direto
    print("\n\n🔐 Testando login direto...")
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"✓ Usuário admin encontrado: {admin.username}")
        print(f"  Email: {admin.email}")
        print(f"  Active: {admin.active}")
        print(f"  Role: {admin.role}")
        
        # Testar senha
        senha_correta = admin.check_password('admin123')
        print(f"  Senha correta (admin123): {senha_correta}")
        
        if not senha_correta:
            print("\n⚠️ PROBLEMA: A senha 'admin123' não bate!")
            print("  Tentando outras senhas possíveis...")
            for pwd in ['123456', 'password', '12345678']:
                if admin.check_password(pwd):
                    print(f"  ✓ Senha que funciona: {pwd}")
    else:
        print("✗ Usuário admin NÃO encontrado!")
    
    # Fazer um teste com a API
    print("\n\n🧪 Testando com client de teste...")
    client = app.test_client()
    
    response = client.post('/api/auth/login',
        data=json.dumps({'username': 'admin', 'password': 'admin123'}),
        content_type='application/json'
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.get_json()}")
    
    if response.status_code != 200:
        print("\n⚠️ Login falhou!")
        print("Verificando erro no servidor...")
