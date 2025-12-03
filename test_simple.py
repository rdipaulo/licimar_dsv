#!/usr/bin/env python
"""
Script simples para testar os 5 problemas
"""
import subprocess
import sys
import time

time.sleep(2)  # Aguardar um pouco para o servidor estar pronto

print("\n=== TESTE 1: Login ===")
resultado = subprocess.run(
    [sys.executable, "-m", "requests", "post", "http://127.0.0.1:5000/api/auth/login",
     "-H", "Content-Type: application/json",
     "-d", '{"username":"admin","password":"admin123"}'],
    capture_output=True,
    text=True
)
print(f"Status: {resultado.returncode}")

# Usar curl em vez disso
print("\n=== TESTE COM CURL ===")
resultado = subprocess.run(
    ['curl', '-X', 'POST', 'http://127.0.0.1:5000/api/auth/login',
     '-H', 'Content-Type: application/json',
     '-d', '{"username":"admin","password":"admin123"}'],
    capture_output=True,
    text=True
)
print(f"Resposta: {resultado.stdout}")
if resultado.stderr:
    print(f"Erro: {resultado.stderr}")
