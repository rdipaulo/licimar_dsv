#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'C:\licimar_dsv\backend\licimar_mvp_app')

from src.main import create_app
from src.models import Produto

app = create_app()

with app.app_context():
    prods = ['Gelo Seco (kg)', 'Caixa de Isopor', 'Sacola Termica']
    for nome in prods:
        p = Produto.query.filter_by(nome=nome).first()
        if p:
            print(f"✅ {p.nome}: nao_devolve={p.nao_devolve}")
        else:
            print(f"❌ {nome}: NÃO ENCONTRADO")
