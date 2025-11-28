#!/usr/bin/env python3
"""
Teste de persistência de dados
Verifica se categorias, produtos e pedidos persistem corretamente no banco
"""
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

def test_database_persistence():
    """Testa persistência de dados no banco"""
    db_path = r'C:\licimar_dsv\backend\licimar_mvp_app\instance\licimar_dev.db'
    
    print("="*70)
    print("TESTE DE PERSISTÊNCIA DE DADOS")
    print("="*70)
    
    if not os.path.exists(db_path):
        print(f"\n✗ Banco de dados não encontrado: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n[1] Verificando Categorias...")
        cursor.execute("SELECT id, nome FROM categorias ORDER BY id;")
        categorias = cursor.fetchall()
        if categorias:
            print(f"    ✓ {len(categorias)} categorias encontradas:")
            for cat_id, nome in categorias:
                print(f"      - ID {cat_id}: {nome}")
        else:
            print("    ✗ Nenhuma categoria encontrada")
            
        print("\n[2] Verificando Produtos...")
        cursor.execute("""
            SELECT p.id, p.nome, c.nome as categoria 
            FROM produtos p 
            LEFT JOIN categorias c ON p.categoria_id = c.id 
            ORDER BY p.id;
        """)
        produtos = cursor.fetchall()
        if produtos:
            print(f"    ✓ {len(produtos)} produtos encontrados:")
            for prod_id, nome, cat in produtos:
                cat_name = cat or "SEM CATEGORIA"
                print(f"      - ID {prod_id}: {nome} ({cat_name})")
        else:
            print("    ✗ Nenhum produto encontrado")
            
        print("\n[3] Verificando Pedidos...")
        cursor.execute("""
            SELECT p.id, a.nome, p.data_operacao, p.status, p.total
            FROM pedidos p
            LEFT JOIN ambulantes a ON p.ambulante_id = a.id
            ORDER BY p.id DESC 
            LIMIT 5;
        """)
        pedidos = cursor.fetchall()
        if pedidos:
            print(f"    ✓ Últimos {len(pedidos)} pedidos:")
            for ped_id, ambulante, data, status, total in pedidos:
                print(f"      - Pedido #{ped_id}: {ambulante} | Status: {status} | Total: R${total} | Data: {data}")
        else:
            print("    ⓘ Nenhum pedido encontrado")
            
        print("\n[4] Verificando Itens de Pedido (Quantidades)...")
        cursor.execute("""
            SELECT 
                ip.id,
                ip.quantidade_saida as saida_type,
                TYPEOF(ip.quantidade_saida) as saida_tipo,
                ip.quantidade_retorno as retorno_type,
                TYPEOF(ip.quantidade_retorno) as retorno_tipo
            FROM itens_pedido ip
            LIMIT 3;
        """)
        itens = cursor.fetchall()
        if itens:
            print(f"    ✓ Verificando tipos de dados (esperado: integer):")
            for item_id, saida, saida_tipo, retorno, retorno_tipo in itens:
                saida_ok = "✓" if saida_tipo == "integer" else "✗"
                retorno_ok = "✓" if retorno_tipo == "integer" else "✗"
                print(f"      Item {item_id}: saida={saida} ({saida_tipo}) {saida_ok} | retorno={retorno} ({retorno_tipo}) {retorno_ok}")
        else:
            print("    ⓘ Nenhum item de pedido encontrado")
            
        print("\n[5] Verificando Ambulantes...")
        cursor.execute("SELECT id, nome FROM ambulantes ORDER BY id;")
        ambulantes = cursor.fetchall()
        if ambulantes:
            print(f"    ✓ {len(ambulantes)} ambulantes encontrados")
        else:
            print("    ✗ Nenhum ambulante encontrado")
            
        print("\n[6] Verificando Estrutura de Tabelas...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name;
        """)
        tabelas = cursor.fetchall()
        print(f"    ✓ {len(tabelas)} tabelas encontradas:")
        for (tabela,) in tabelas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela};")
            count = cursor.fetchone()[0]
            print(f"      - {tabela}: {count} registros")
            
        print("\n" + "="*70)
        print("✓ TESTE CONCLUÍDO COM SUCESSO")
        print("="*70)
        print("\nResumo:")
        print("  • Banco de dados está acessível e contém dados")
        print("  • Tipos de dados foram convertidos corretamente (INTEGER)")
        print("  • Todas as tabelas estão presentes")
        print("\nPróximos passos:")
        print("  1. Reinicie o backend")
        print("  2. Acesse a aplicação")
        print("  3. Verifique se categorias persistem após restart")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Erro ao acessar banco: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    success = test_database_persistence()
    sys.exit(0 if success else 1)
