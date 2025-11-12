#!/usr/bin/env python3
"""
Ponto de entrada da aplicação Flask Licimar MVP
"""
import os
from src.main import create_app

# Criar a aplicação Flask
app = create_app()

if __name__ == '__main__':
    # Configurações para desenvolvimento
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("=" * 60)
    print("LICIMAR MVP - Sistema de Gestão de Ambulantes")
    print("=" * 60)
    print(f"Servidor iniciando na porta {port}")
    print(f"Modo debug: {debug}")
    print(f"Acesse: http://localhost:{port}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
