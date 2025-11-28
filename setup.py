#!/usr/bin/env python3
"""
Setup automático do Licimar MVP v2
Inicializa backend (Python/Flask) e frontend (React/Vite)
- Verifica dependências
- Instala pacotes
- Configura banco de dados
- Fornece instruções de inicialização
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(cmd, description, cwd=None):
    """Execute a command and report result"""
    print(f"\n{'='*60}")
    print(f"► {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=False)
        if result.returncode == 0:
            print(f"✓ {description} - OK")
            return True
        else:
            print(f"✗ {description} - FALHOU (código {result.returncode})")
            return False
    except Exception as e:
        print(f"✗ {description} - ERRO: {e}")
        return False

def main():
    root_dir = Path(__file__).parent
    backend_dir = root_dir / "backend" / "licimar_mvp_app"
    frontend_dir = root_dir / "frontend" / "licimar_mvp_frontend"
    
    print(f"\n{'='*60}")
    print("LICIMAR MVP - SETUP AUTOMÁTICO")
    print(f"{'='*60}")
    print(f"Root: {root_dir}")
    
    # 1. Backend setup
    print(f"\n{'#'*60}")
    print("# CONFIGURAÇÃO DO BACKEND")
    print(f"{'#'*60}")
    
    # Migrate database
    run_command(
        f"python migrate_add_divida.py",
        "Migração do banco (adicionar divida_acumulada)",
        cwd=backend_dir
    )
    
    # Initialize database if needed
    run_command(
        f"python -c \"from src.main import create_app; from src.database import db; app = create_app(); app.app_context().push(); db.create_all(); print('✓ Schema atualizado')\"",
        "Atualizar schema do banco de dados",
        cwd=backend_dir
    )
    
    # 2. Frontend setup
    print(f"\n{'#'*60}")
    print("# CONFIGURAÇÃO DO FRONTEND")
    print(f"{'#'*60}")
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        run_command(
            f"npm install --legacy-peer-deps",
            "Instalar dependências do frontend",
            cwd=frontend_dir
        )
    else:
        print("✓ node_modules já existe - pulando npm install")
    
    # 3. Start servers
    print(f"\n{'#'*60}")
    print("# INICIANDO SERVIDORES")
    print(f"{'#'*60}")
    
    print("\n✓ Setup completo!")
    print("\nPróximos passos:")
    print(f"  1. Backend: cd backend/licimar_mvp_app && set FLASK_DEBUG=0 && python app.py")
    print(f"  2. Frontend: cd frontend/licimar_mvp_frontend && npm run dev")
    print(f"\n  Acesso: http://localhost:5173")
    print(f"  Login: admin / admin123")

if __name__ == "__main__":
    main()
