#!/usr/bin/env python3
"""Verificar pedidos no banco"""
from src.main import create_app
from src.models import Pedido, Ambulante

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("VERIFICAÇÃO DE DADOS DE TESTE")
    print("="*60)
    
    # Pedidos
    pedidos = Pedido.query.all()
    print(f"\nTotal de pedidos: {len(pedidos)}")
    if pedidos:
        for i, p in enumerate(pedidos[:5], 1):
            ambulante_nome = p.ambulante.nome if p.ambulante else "N/A"
            print(f"  {i}. ID: {p.id} | Ambulante: {ambulante_nome} | Status: {p.status} | Total: R$ {float(p.total):.2f}")
        if len(pedidos) > 5:
            print(f"  ... e mais {len(pedidos) - 5} pedidos")
    
    # Dívidas
    ambulantes_divida = Ambulante.query.filter(Ambulante.divida_acumulada > 0).all()
    print(f"\nAmbuantes com dívida: {len(ambulantes_divida)}")
    if ambulantes_divida:
        total_divida = sum(float(a.divida_acumulada or 0) for a in ambulantes_divida)
        print(f"Total acumulado: R$ {total_divida:.2f}")
        for a in ambulantes_divida[:5]:
            print(f"  - {a.nome}: R$ {float(a.divida_acumulada or 0):.2f}")
    
    print("\n" + "="*60)

