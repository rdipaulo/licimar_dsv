#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpar histórico de testes do Licimar MVP

Opções:
  python clean_history.py listar-pedidos     - Lista todos os pedidos
  python clean_history.py limpar-pedidos     - Deleta TODOS os pedidos
  python clean_history.py limpar-dividas     - Reseta divida_acumulada para 0
  python clean_history.py limpar-tudo        - Deleta pedidos E reseta dívidas
  python clean_history.py resetar-db         - Reseta banco inteiro (CUIDADO!)
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend' / 'licimar_mvp_app'))

from src.database import db
from src.main import create_app
from src.models import Pedido, Ambulante
from sqlalchemy import text


def print_header(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}\n")


def print_success(msg):
    print(f"[OK] {msg}")


def print_warn(msg):
    print(f"[!] {msg}")


def print_error(msg):
    print(f"[ERR] {msg}")


def listar_pedidos(app):
    """Lista todos os pedidos registrados"""
    print_header("Listando Pedidos")
    
    with app.app_context():
        pedidos = Pedido.query.all()
        
        if not pedidos:
            print_warn("Nenhum pedido registrado")
            return
        
        print(f"Total de pedidos: {len(pedidos)}\n")
        
        for pedido in pedidos:
            print(f"ID: {pedido.id}")
            print(f"  Ambulante: {pedido.ambulante.nome if pedido.ambulante else 'N/A'}")
            print(f"  Data Operacao: {pedido.data_operacao}")
            print(f"  Status: {pedido.status}")
            print(f"  Total: R$ {float(pedido.total):.2f}")
            print(f"  Criado em: {pedido.created_at}\n")


def limpar_pedidos(app):
    """Deleta TODOS os pedidos do banco"""
    print_header("Limpando Histórico de Pedidos")
    
    with app.app_context():
        count = Pedido.query.count()
        
        if count == 0:
            print_warn("Nenhum pedido para deletar")
            return
        
        print(f"Serão deletados {count} pedido(s)")
        confirmacao = input("Tem certeza? (s/n): ").lower().strip()
        
        if confirmacao != 's':
            print_warn("Operação cancelada")
            return
        
        try:
            # Delete all pedidos
            db.session.query(Pedido).delete()
            db.session.commit()
            print_success(f"Deletados {count} pedido(s)")
        except Exception as e:
            db.session.rollback()
            print_error(f"Erro ao deletar: {e}")


def limpar_dividas(app):
    """Reseta divida_acumulada de todos os ambulantes para 0"""
    print_header("Resetando Dívidas Acumuladas")
    
    with app.app_context():
        ambulantes = Ambulante.query.all()
        
        if not ambulantes:
            print_warn("Nenhum ambulante registrado")
            return
        
        total_divida = sum(float(a.divida_acumulada or 0) for a in ambulantes)
        count_divida = sum(1 for a in ambulantes if (a.divida_acumulada or 0) > 0)
        
        if count_divida == 0:
            print_warn("Nenhuma dívida registrada")
            return
        
        print(f"Total de dívida: R$ {total_divida:.2f}")
        print(f"Ambulantes com dívida: {count_divida}")
        confirmacao = input("Tem certeza em resetar? (s/n): ").lower().strip()
        
        if confirmacao != 's':
            print_warn("Operação cancelada")
            return
        
        try:
            for ambulante in ambulantes:
                if ambulante.divida_acumulada and ambulante.divida_acumulada > 0:
                    print(f"  {ambulante.nome}: R$ {ambulante.divida_acumulada:.2f} → R$ 0.00")
                    ambulante.divida_acumulada = 0
            
            db.session.commit()
            print_success(f"Dívidas resetadas para {count_divida} ambulante(s)")
        except Exception as e:
            db.session.rollback()
            print_error(f"Erro ao resetar: {e}")


def limpar_tudo(app):
    """Deleta pedidos E reseta dívidas"""
    print_header("Limpando TUDO (Pedidos + Dívidas)")
    
    print("Isso vai:")
    print("  1. Deletar TODOS os pedidos")
    print("  2. Resetar TODAS as dívidas para 0")
    confirmacao = input("\nTem certeza? (s/n): ").lower().strip()
    
    if confirmacao != 's':
        print_warn("Operação cancelada")
        return
    
    limpar_pedidos(app)
    limpar_dividas(app)


def resetar_db(app):
    """Reseta banco inteiro - CUIDADO!"""
    print_header("⚠ RESETANDO BANCO INTEIRO ⚠")
    
    print("ATENÇÃO: Isso vai DELETAR TUDO e recriar com dados de teste!")
    print("Todos os pedidos, dívidas e dados customizados serão perdidos!")
    
    confirmacao = input("\nDigite 'SIM, RESETAR' para confirmar: ").strip()
    
    if confirmacao != 'SIM, RESETAR':
        print_warn("Operação cancelada")
        return
    
    try:
        with app.app_context():
            print("Dropando todas as tabelas...")
            db.drop_all()
            
            print("Criando tabelas...")
            db.create_all()
            
            # Aqui você pode importar dados iniciais se necessário
            # from src.models import Usuario
            # admin = Usuario(username='admin', email='admin@licimar.com', role='admin')
            # admin.set_password('admin123')
            # db.session.add(admin)
            # db.session.commit()
            
            print_success("Banco resetado com sucesso!")
            print_warn("Você precisa reinicializar dados com: python init_database.py")
    except Exception as e:
        db.session.rollback()
        print_error(f"Erro ao resetar: {e}")


def main():
    app = create_app()
    
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    comando = sys.argv[1].lower()
    
    if comando == 'listar-pedidos':
        listar_pedidos(app)
    elif comando == 'limpar-pedidos':
        limpar_pedidos(app)
    elif comando == 'limpar-dividas':
        limpar_dividas(app)
    elif comando == 'limpar-tudo':
        limpar_tudo(app)
    elif comando == 'resetar-db':
        resetar_db(app)
    else:
        print(f"Comando desconhecido: {comando}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
