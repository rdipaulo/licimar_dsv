#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migração para adicionar tabelas de Dívidas e Consignação
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import create_app
from src.database import db
from src.models import Divida, PagamentoDivida, PedidoConsignacao, ItemPedidoConsignacao

def migrate():
    """Executar migração"""
    app = create_app('development')
    
    with app.app_context():
        print("[MIGRATE] Criando tabelas de Dívidas e Consignação...")
        
        try:
            # Criar as novas tabelas
            db.create_all()
            
            print("  ✅ Tabela 'dividas' criada")
            print("  ✅ Tabela 'pagamentos_divida' criada")
            print("  ✅ Tabela 'pedidos_consignacao' criada")
            print("  ✅ Tabela 'itens_pedido_consignacao' criada")
            
            print("\n[SUCCESS] Migração concluída com sucesso!")
            print("\n📋 Resumo das tabelas criadas:")
            print("  • dividas: Registro de dívidas de clientes")
            print("  • pagamentos_divida: Registro de abatimentos de dívidas")
            print("  • pedidos_consignacao: Pedidos de consignação (cabeçalho)")
            print("  • itens_pedido_consignacao: Itens de pedidos de consignação")
            print("\n🔗 Relacionamentos configurados:")
            print("  • Cliente → Dívidas (one-to-many)")
            print("  • Dívida → Pagamentos (one-to-many)")
            print("  • Cliente → Pedidos Consignação (one-to-many)")
            print("  • Pedido Consignação → Itens (one-to-many)")
            print("  • Produto → Itens Consignação (one-to-many)")
            
        except Exception as e:
            print(f"  ❌ Erro durante migração: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    migrate()
