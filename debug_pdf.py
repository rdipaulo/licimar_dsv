#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug PDF diretamente no contexto da app"""
import sys
sys.path.insert(0, r'C:\licimar_dsv\backend\licimar_mvp_app')

from src.main import create_app
from src.models import Pedido
from flask import render_template

app = create_app()

with app.app_context():
    pedido = Pedido.query.first()
    
    if not pedido:
        print("❌ Nenhum pedido encontrado")
        exit(1)
    
    print(f"Pedido: {pedido.id}")
    print(f"Itens: {len(pedido.itens)}")
    
    try:
        # Simulate what the route does
        itens_html = ''.join([
            f'''
            <tr>
                <td>{item.produto.nome}</td>
                <td>{float(item.quantidade_saida):.3f}</td>
                <td>R$ {float(item.preco_unitario):.2f}</td>
                <td>R$ {float(float(item.quantidade_saida) * float(item.preco_unitario)):.2f}</td>
            </tr>
            '''
            for item in pedido.itens
        ])
        
        print(f"✅ itens_html gerado: {len(itens_html)} caracteres")
        
        html_content = render_template(
            'nota_fiscal_saida.html',
            pedido=pedido,
            itens_html=itens_html
        )
        
        print(f"✅ Template renderizado: {len(html_content)} caracteres")
        print(f"\nPrimeiros 200 caracteres do HTML:")
        print(html_content[:200])
        
        # Try to generate PDF
        from weasyprint import HTML
        
        html = HTML(string=html_content)
        print(f"✅ HTML object created")
        
        pdf = html.write_pdf()
        print(f"✅ PDF gerado: {len(pdf)} bytes")
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
