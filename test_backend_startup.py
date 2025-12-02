#!/usr/bin/env python3
"""
Teste rapido executando apos backend estar pronto
"""
import subprocess
import time
import requests
import sys
import os

os.chdir('backend/licimar_mvp_app')

# Inicia backend em background
print("Iniciando backend...")
backend_process = subprocess.Popen(
    [sys.executable, 'app.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Aguarda backend inicializar
print("Aguardando 5 segundos para backend inicializar...")
time.sleep(5)

# Verifica se backend está rodando
try:
    response = requests.get('http://127.0.0.1:5000/api/health', timeout=5)
    print(f"[OK] Backend respondendo! Status: {response.status_code}")
    print(response.json())
except Exception as e:
    print(f"[ERROR] Backend nao respondendo: {e}")
    # Obtém output do backend
    try:
        stdout, stderr = backend_process.communicate(timeout=1)
        print("\n=== STDOUT ===")
        print(stdout)
        print("\n=== STDERR ===")
        print(stderr)
    except subprocess.TimeoutExpired:
        print("Backend ainda rodando...")
    backend_process.terminate()
    sys.exit(1)

# Se chegou aqui, backend está pronto
print("\nBackend esta pronto! Mantendo rodando...")
print("Pressione Ctrl+C para encerrar")

try:
    backend_process.wait()
except KeyboardInterrupt:
    print("\nEncerrando...")
    backend_process.terminate()
    backend_process.wait()
