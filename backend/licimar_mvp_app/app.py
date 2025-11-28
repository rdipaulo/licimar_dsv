#!/usr/bin/env python3
"""
Ponto de entrada da aplicação Flask Licimar MVP
"""
import os
import sys
import traceback

try:
    from src.main import create_app
    
    # Criar a aplicação Flask
    print("[STARTUP] Criando aplicação Flask...", flush=True)
    app = create_app()
    print("[STARTUP] Aplicação Flask criada com sucesso!", flush=True)
    
except Exception as e:
    print(f"[ERROR] Erro ao criar aplicação: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

if __name__ == '__main__':
    try:
        # Configurações para desenvolvimento
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        print("=" * 60, flush=True)
        print("LICIMAR MVP - Sistema de Gestão de Ambulantes", flush=True)
        print("=" * 60, flush=True)
        print(f"[STARTUP] Servidor iniciando na porta {port}", flush=True)
        print(f"[STARTUP] Modo debug: {debug}", flush=True)
        print(f"[STARTUP] Acesse: http://localhost:{port}", flush=True)
        print("=" * 60, flush=True)
        
        app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)
        
    except Exception as e:
        print(f"[ERROR] Erro ao iniciar servidor: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)
