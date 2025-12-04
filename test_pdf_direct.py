#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Teste do PDF diretamente sem HTTP"""
import sys
sys.path.insert(0, r'C:\licimar_dsv\backend\licimar_mvp_app')

from src.main import create_app
from src.models import Pedido
from fpdf import FPDF

app = create_app()

with app.app_context():
    pedido = Pedido.query.first()
    if not pedido:
        print("[ERRO] Nenhum pedido")
        exit(1)
    
    try:
        # Simular o que a rota faz
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'NOTA FISCAL DE SAIDA - Pedido #{}'.format(pedido.id), ln=True, align='C')
        
        pdf.set_font('Arial', '', 10)
        pdf.ln(10)
        
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, 'Cliente: {}'.format(pedido.cliente.nome), ln=True)
        pdf.cell(0, 5, 'Total: R$ {:.2f}'.format(float(pedido.total)), ln=True)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(60, 8, 'Produto', border=1)
        pdf.cell(30, 8, 'Qtd', border=1, align='C')
        pdf.cell(30, 8, 'Preco', border=1, align='C')
        pdf.cell(30, 8, 'Total', border=1, align='C')
        pdf.ln()
        
        pdf.set_font('Arial', '', 9)
        for item in pedido.itens:
            quantidade = float(item.quantidade_saida)
            preco = float(item.preco_unitario)
            total = quantidade * preco
            
            pdf.cell(60, 8, item.produto.nome[:30], border=1)
            pdf.cell(30, 8, '{:.3f}'.format(quantidade), border=1, align='C')
            pdf.cell(30, 8, '{:.2f}'.format(preco), border=1, align='C')
            pdf.cell(30, 8, '{:.2f}'.format(total), border=1, align='C')
            pdf.ln()
        
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 8, 'TOTAL: R$ {:.2f}'.format(float(pedido.total)), align='R')
        
        # Output PDF
        pdf_bytes = pdf.output()
        print("[OK] PDF gerado: {} bytes".format(len(pdf_bytes)))
        
        # Verificar se é valido
        if b'%PDF' in pdf_bytes[:10]:
            print("[OK] PDF valido (comeca com %PDF)")
        else:
            print("[ERRO] PDF invalido")
            print("Primeiros 50 bytes: {}".format(pdf_bytes[:50]))
            
    except Exception as e:
        print("[ERRO] {}".format(e))
        import traceback
        traceback.print_exc()
