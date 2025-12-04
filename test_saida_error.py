#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Teste com erro traceback"""
import sys
sys.path.insert(0, r'C:\licimar_dsv\backend\licimar_mvp_app')

from src.main import create_app
from src.models import Cliente, Produto
from src.database import db
from decimal import Decimal

app = create_app()

with app.app_context():
    cliente = Cliente.query.first()
    gelo = Produto.query.filter_by(nome='Gelo Seco (kg)').first()
    
    print(f"Cliente: {cliente.nome}")
    print(f"Gelo: {gelo.nome}")
    print(f"Gelo preco type: {type(gelo.preco)} = {gelo.preco}")
    
    # Simulate what the route does
    quantidade_saida = 2.5
    print(f"\nTesting calculation:")
    print(f"  quantidade_saida: {quantidade_saida} (type: {type(quantidade_saida).__name__})")
    print(f"  preco: {gelo.preco} (type: {type(gelo.preco).__name__})")
    
    try:
        result = float(quantidade_saida) * float(gelo.preco)
        print(f"  ✅ Result: {result} (type: {type(result).__name__})")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
