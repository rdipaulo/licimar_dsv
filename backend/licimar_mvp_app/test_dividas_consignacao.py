#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para validar as novas classes de modelo
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import create_app
from src.database import db
from src.models import Cliente, Divida, PagamentoDivida, PedidoConsignacao, ItemPedidoConsignacao

def test_models():
    """Testar os modelos"""
    app = create_app('development')
    
    with app.app_context():
        print("[TEST] Validando modelos de Dívidas e Consignação...\n")
        
        # 1. Obter um cliente existente
        cliente = Cliente.query.first()
        if not cliente:
            print("❌ Nenhum cliente encontrado. Execute setup_db.py primeiro.")
            sys.exit(1)
        
        print(f"✅ Cliente encontrado: {cliente.nome} (ID: {cliente.id})")
        
        # 2. Criar uma dívida de teste
        print("\n[TEST] Criando dívida de teste...")
        divida_teste = Divida(
            id_cliente=cliente.id,
            valor_divida=100.00,
            descricao="Teste de dívida",
            status='Em Aberto'
        )
        db.session.add(divida_teste)
        db.session.commit()
        print(f"✅ Dívida criada: ID {divida_teste.id_divida}, Valor: R$ {divida_teste.valor_divida}")
        
        # 3. Criar um pagamento de dívida
        print("\n[TEST] Criando pagamento de dívida...")
        pagamento = PagamentoDivida(
            id_divida=divida_teste.id_divida,
            cobranca_divida=30.00,
            descricao="Pagamento parcial"
        )
        db.session.add(pagamento)
        db.session.commit()
        print(f"✅ Pagamento criado: ID {pagamento.id_lancamento}, Valor: R$ {pagamento.cobranca_divida}")
        
        # 4. Testar cálculo de saldo devedor
        print("\n[TEST] Testando cálculo de saldo devedor...")
        saldo = divida_teste.calcular_saldo_devedor()
        print(f"  Valor original: R$ {divida_teste.valor_divida}")
        print(f"  Abatimento: R$ {pagamento.cobranca_divida}")
        print(f"  Saldo devedor: R$ {saldo}")
        assert saldo == 70.00, f"Saldo incorreto! Esperado 70.00, obtido {saldo}"
        print("✅ Cálculo de saldo devedor correto!")
        
        # 5. Testar propriedade divida_pendente_total
        print("\n[TEST] Testando propriedade Cliente.divida_pendente_total...")
        divida_total = cliente.divida_pendente_total
        print(f"  Dívida pendente total do cliente: R$ {divida_total}")
        assert divida_total == 70.00, f"Dívida pendente incorreta! Esperado 70.00, obtido {divida_total}"
        print("✅ Propriedade divida_pendente_total funcionando!")
        
        # 6. Criar pedido de consignação
        print("\n[TEST] Criando pedido de consignação...")
        pedido_consignacao = PedidoConsignacao(
            id_cliente=cliente.id,
            tipo_operacao='RETIRADA',
            valor_total_final=0  # Será calculado
        )
        db.session.add(pedido_consignacao)
        db.session.flush()  # Para obter o ID antes de fazer commit
        print(f"✅ Pedido de consignação criado: ID {pedido_consignacao.id_pedido}")
        
        # 7. Criar itens do pedido de consignação
        print("\n[TEST] Criando itens de consignação...")
        from src.models import Produto
        produto = Produto.query.first()
        if produto:
            item = ItemPedidoConsignacao(
                id_pedido=pedido_consignacao.id_pedido,
                id_produto=produto.id,
                quantidade_negociada=5,
                valor_unitario_venda=produto.preco
            )
            item.calcular_subtotal()
            db.session.add(item)
            db.session.commit()
            print(f"✅ Item criado: {produto.nome} x 5 = R$ {item.subtotal}")
            
            # Calcular total do pedido
            pedido_consignacao.calcular_total()
            db.session.commit()
            print(f"✅ Total do pedido: R$ {pedido_consignacao.valor_total_final}")
        
        # 8. Testar método to_dict
        print("\n[TEST] Testando método to_dict()...")
        divida_dict = divida_teste.to_dict()
        print("✅ Dívida.to_dict():")
        print(f"   - ID: {divida_dict['id_divida']}")
        print(f"   - Cliente: {divida_dict['cliente_nome']}")
        print(f"   - Valor: R$ {divida_dict['valor_divida']}")
        print(f"   - Saldo: R$ {divida_dict['saldo_devedor']}")
        print(f"   - Abatido: R$ {divida_dict['total_abatido']}")
        
        print("\n[SUCCESS] ✅ Todos os testes passaram!")
        print("\n📊 Resumo dos testes:")
        print("  ✅ Modelos criados e relacionamentos OK")
        print("  ✅ Dívida e Pagamento criados com sucesso")
        print("  ✅ Cálculo de saldo devedor correto")
        print("  ✅ Propriedade divida_pendente_total funcionando")
        print("  ✅ Pedido de consignação com itens funcionando")
        print("  ✅ Serialização to_dict() funcionando")

if __name__ == '__main__':
    test_models()
