#!/usr/bin/env python3
"""
Script para iniciar o backend e manter rodando
"""
import os
import subprocess
import sys
import time

os.chdir('backend/licimar_mvp_app')

try:
    print("Iniciando backend Licimar MVP...")
    print("="*60)
    
    # Executa o app.py
    process = subprocess.Popen(
        [sys.executable, 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Aguarda e exibe saída
    while True:
        line = process.stdout.readline()
        if line:
            print(line, end='')
        else:
            if process.poll() is not None:
                break
                
except KeyboardInterrupt:
    print("\nEncerrando backend...")
    process.terminate()
    process.wait()
    print("Backend encerrado")
    sys.exit(0)
except Exception as e:
    print(f"Erro ao iniciar backend: {e}")
    sys.exit(1)
