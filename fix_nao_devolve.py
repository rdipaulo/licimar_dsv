#!/usr/bin/env python
"""Corrigir campo nao_devolve para gelo e caixa de isopor"""
import sys
sys.path.insert(0, 'C:\\licimar_dsv\\backend\\licimar_mvp_app')

import os
os.chdir('C:\\licimar_dsv\\backend\\licimar_mvp_app')

from src.database import db
from src.main import create_app
from src.models import Produto

app = create_app()

with app.app_context():
    # Marcar Gelo e Caixa de Isopor como não devolvíveis
    gelo = Produto.query.filter(Produto.nome.ilike('%gelo%')).first()
    caixa = Produto.query.filter(Produto.nome.ilike('%isopor%')).first()
    
    if gelo:
        gelo.nao_devolve = True
        print(f"✓ {gelo.nome} marcado como NÃO DEVOLVÍVEL")
    
    if caixa:
        caixa.nao_devolve = True
        print(f"✓ {caixa.nome} marcado como NÃO DEVOLVÍVEL")
    
    db.session.commit()
    print("\n✓ Banco de dados atualizado!")
