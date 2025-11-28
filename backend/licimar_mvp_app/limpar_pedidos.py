#!/usr/bin/env python3
"""
Script para listar e limpar pedidos de teste
"""
import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import create_app
from src.database import db
from src.models import Pedido

def listar_pedidos():
    """Lista todos os pedidos no banco"""
    app = create_app('development')
    
    with app.app_context():
        pedidos = Pedido.query.all()
        
        if not pedidos:
            print("Nenhum pedido encontrado")
            return
        
        print("\n" + "="*80)
        print("LISTA DE PEDIDOS")
        print("="*80)
        
        for pedido in pedidos:
            print(f"\nID: {pedido.id}")
            print(f"  Ambulante: {pedido.ambulante.nome if pedido.ambulante else 'N/A'}")
            print(f"  Tipo: {pedido.tipo}")
            print(f"  Status: {pedido.status}")
            print(f"  Total: R$ {pedido.total_venda:.2f}")
            print(f"  Data: {pedido.created_at}")

def deletar_pedido(pedido_id):
    """Deleta um pedido específico"""
    app = create_app('development')
    
    with app.app_context():
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            print(f"❌ Pedido {pedido_id} não encontrado")
            return
        
        ambulante_nome = pedido.ambulante.nome if pedido.ambulante else 'N/A'
        db.session.delete(pedido)
        db.session.commit()
        
        print(f"✓ Pedido {pedido_id} (Ambulante: {ambulante_nome}) deletado com sucesso")

def limpar_todos_pedidos():
    """Deleta todos os pedidos"""
    app = create_app('development')
    
    with app.app_context():
        count = Pedido.query.count()
        
        if count == 0:
            print("Nenhum pedido para deletar")
            return
        
        if input(f"\nTem certeza que deseja deletar {count} pedidos? (s/n): ").lower() != 's':
            print("Operação cancelada")
            return
        
        Pedido.query.delete()
        db.session.commit()
        
        print(f"✓ {count} pedidos deletados com sucesso")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciar pedidos de teste')
    parser.add_argument('comando', choices=['listar', 'deletar', 'limpar'], help='Comando a executar')
    parser.add_argument('--id', type=int, help='ID do pedido (para deletar)')
    
    args = parser.parse_args()
    
    if args.comando == 'listar':
        listar_pedidos()
    elif args.comando == 'deletar':
        if not args.id:
            print("❌ Especifique --id para deletar um pedido")
            print("Exemplo: python limpar_pedidos.py deletar --id 5")
        else:
            deletar_pedido(args.id)
    elif args.comando == 'limpar':
        limpar_todos_pedidos()
