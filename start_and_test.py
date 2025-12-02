#!/usr/bin/env python3
"""Iniciar backend e testar"""
import subprocess
import time
import requests
import json

print("Iniciando backend...")
proc = subprocess.Popen(
    ["python", "app.py"],
    cwd=r"C:\licimar_dsv\backend\licimar_mvp_app",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Aguarda inicialização
print("Aguardando 5 segundos...")
time.sleep(5)

print("Testando login...")
try:
    response = requests.post(
        "http://127.0.0.1:5000/api/auth/login",
        json={"username": "admin", "password": "admin123"},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"Erro ao conectar: {e}")
    print("\nOutput do backend:")
    proc.terminate()
    stdout, stderr = proc.communicate(timeout=2)
    print(stdout)
    if stderr:
        print("STDERR:")
        print(stderr)
