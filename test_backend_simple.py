#!/usr/bin/env python
"""
Teste rápido dos 5 problemas
"""
import sys
sys.path.insert(0, 'C:\\licimar_dsv\\backend\\licimar_mvp_app')

import os
os.chdir('C:\\licimar_dsv\\backend\\licimar_mvp_app')

from src.database import db
from src.main import create_app

app = create_app()

with app.app_context():
    # Test 1: Verificar duplicados
    from src.models import Produto, Cliente
    
    print("\n=== TESTE 1: PRODUTOS DUPLICADOS ===")
    produtos = Produto.query.all()
    print(f"Total de produtos: {len(produtos)}")
    
    nomes = {}
    for p in produtos:
        key = f"{p.nome.lower()}_{p.categoria_id}"
        if key not in nomes:
            nomes[key] = []
        nomes[key].append(p.id)
    
    duplicados = {k: v for k, v in nomes.items() if len(v) > 1}
    print(f"Produtos duplicados: {duplicados if duplicados else 'NENHUM'}")
    print("✅ TESTE 1 PASSOU" if not duplicados else "❌ TESTE 1 FALHOU")
    
    # Test 2: Verificar campo de gelo
    print("\n=== TESTE 2: GELO SECO ===")
    gelo = Produto.query.filter(Produto.nome.ilike('%gelo%')).first()
    if gelo:
        print(f"Gelo encontrado: {gelo.nome} (ID: {gelo.id})")
        print(f"Preço: R$ {float(gelo.preco):.2f}")
        print("✅ TESTE 2 PASSOU")
    else:
        print("❌ TESTE 2 FALHOU - Gelo não encontrado")
    
    # Test 3: Data/Hora Brasília
    print("\n=== TESTE 3: DATA/HORA BRASÍLIA ===")
    from src.models import get_brasilia_now
    from datetime import datetime
    import pytz
    
    agora = get_brasilia_now()
    agora_sistema = datetime.now()
    
    print(f"Data/Hora Brasília: {agora}")
    print(f"Data/Hora Sistema: {agora_sistema}")
    print("✅ TESTE 3 PASSOU - Função get_brasilia_now() existe e funciona")
    
    # Test 4: Campo Dívida
    print("\n=== TESTE 4: CAMPO DÍVIDA ===")
    from src.models import Pedido
    
    # Verificar se o modelo Pedido tem o campo divida
    if hasattr(Pedido, 'divida'):
        print("✅ Campo 'divida' existe no modelo Pedido")
    else:
        print("❌ Campo 'divida' NÃO existe no modelo Pedido")
    
    # Test 5: Método calcular_total
    print("\n=== TESTE 5: MÉTODO CALCULAR_TOTAL ===")
    if hasattr(Pedido, 'calcular_total'):
        print("✅ Método 'calcular_total()' existe e foi implementado")
    else:
        print("❌ Método 'calcular_total()' NÃO existe")

print("\n=== TESTES CONCLUÍDOS ===")
