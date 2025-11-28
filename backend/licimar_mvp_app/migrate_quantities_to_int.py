#!/usr/bin/env python3
"""
Script de migração para converter quantidade_saida e quantidade_retorno de NUMERIC para INTEGER
Este script preserva os dados existentes
"""
import os
import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import create_app
from src.database import db
from src.models import ItemPedido

def migrate_quantities_to_int():
    """Migra quantidade_saida e quantidade_retorno para INTEGER"""
    app = create_app('development')
    
    with app.app_context():
        print("="*60)
        print("Migração: Convertendo quantidades para INTEGER")
        print("="*60)
        
        # Usar SQL direto para alterar colunas
        db_path = os.path.join(app.instance_path, 'licimar_dev.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            print("\n[1] Verificando estrutura atual...")
            cursor.execute("PRAGMA table_info(itens_pedido);")
            columns = cursor.fetchall()
            print(f"    Colunas na tabela itens_pedido: {len(columns)}")
            for col in columns:
                print(f"      - {col[1]}: {col[2]}")
            
            print("\n[2] Salvando dados existentes...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS itens_pedido_backup AS
                SELECT * FROM itens_pedido;
            """)
            conn.commit()
            print("    ✓ Backup criado")
            
            print("\n[3] Recreando tabela com tipos corretos...")
            cursor.execute("""
                CREATE TABLE itens_pedido_new (
                    id INTEGER PRIMARY KEY,
                    pedido_id INTEGER NOT NULL,
                    produto_id INTEGER NOT NULL,
                    quantidade_saida INTEGER NOT NULL DEFAULT 0,
                    quantidade_retorno INTEGER NOT NULL DEFAULT 0,
                    preco_unitario NUMERIC NOT NULL,
                    created_at DATETIME,
                    FOREIGN KEY(pedido_id) REFERENCES pedidos(id),
                    FOREIGN KEY(produto_id) REFERENCES produtos(id)
                );
            """)
            conn.commit()
            print("    ✓ Nova tabela criada")
            
            print("\n[4] Copiando dados com conversão...")
            cursor.execute("""
                INSERT INTO itens_pedido_new 
                SELECT 
                    id,
                    pedido_id,
                    produto_id,
                    CAST(ROUND(quantidade_saida) AS INTEGER),
                    CAST(ROUND(quantidade_retorno) AS INTEGER),
                    preco_unitario,
                    created_at
                FROM itens_pedido;
            """)
            count = cursor.rowcount
            conn.commit()
            print(f"    ✓ {count} linhas copiadas com conversão")
            
            print("\n[5] Removendo tabela antiga...")
            cursor.execute("DROP TABLE itens_pedido;")
            conn.commit()
            print("    ✓ Tabela antiga removida")
            
            print("\n[6] Renomeando nova tabela...")
            cursor.execute("ALTER TABLE itens_pedido_new RENAME TO itens_pedido;")
            conn.commit()
            print("    ✓ Tabela renomeada")
            
            print("\n[7] Verificando integridade...")
            cursor.execute("SELECT COUNT(*) FROM itens_pedido;")
            total = cursor.fetchone()[0]
            print(f"    ✓ Total de registros: {total}")
            
            print("\n[8] Reorganizando índices...")
            cursor.execute("VACUUM;")
            conn.commit()
            print("    ✓ Índices otimizados")
            
            print("\n" + "="*60)
            print("✓ Migração concluída com sucesso!")
            print("="*60)
            print("\nDados salvos em backup:")
            print("  Tabela: itens_pedido_backup")
            print(f"  Banco: {db_path}")
            print("\nPróximo passo:")
            print("  1. Reinicie o backend: python app.py")
            print("  2. Teste as funcionalidades de saída e retorno")
            
        except Exception as e:
            conn.rollback()
            print(f"\n✗ Erro durante migração: {e}")
            print("\nTentando reverter...")
            try:
                cursor.execute("DROP TABLE IF EXISTS itens_pedido_new;")
                conn.commit()
            except:
                pass
            return False
        finally:
            conn.close()
        
        return True

if __name__ == '__main__':
    success = migrate_quantities_to_int()
    sys.exit(0 if success else 1)
