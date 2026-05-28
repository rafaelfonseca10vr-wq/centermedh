#!/usr/bin/env python3
"""
Script para criar vendas de teste com parcelas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Venda, Cliente, Vendedor, Produto, ItemVenda, ContaReceber
from datetime import datetime, timedelta

def criar_vendas_teste():
    """Cria vendas de teste com parcelas"""
    
    with app.app_context():
        # Verificar se há clientes e vendedores
        clientes = Cliente.query.all()
        vendedores = Vendedor.query.all()
        produtos = Produto.query.all()
        
        if not clientes:
            print("❌ Nenhum cliente encontrado! Crie clientes primeiro.")
            return
        
        if not vendedores:
            print("❌ Nenhum vendedor encontrado! Crie vendedores primeiro.")
            return
        
        if not produtos:
            print("❌ Nenhum produto encontrado! Crie produtos primeiro.")
            return
        
        print("✅ Dados encontrados:")
        print(f"   Clientes: {len(clientes)}")
        print(f"   Vendedores: {len(vendedores)}")
        print(f"   Produtos: {len(produtos)}")
        
        # Criar vendas de teste
        print("\n=== CRIANDO VENDAS DE TESTE ===")
        
        # Venda 1 - Parcelada (3x)
        cliente1 = clientes[0]
        vendedor1 = vendedores[0]
        produto1 = produtos[0]
        
        venda1 = Venda(
            numero_venda="1",
            cliente_id=cliente1.id,
            vendedor_id=vendedor1.id,
            data_venda=datetime.now(),
            subtotal=300.00,
            desconto=0,
            total=300.00,
            forma_pagamento="PIX",
            tipo_parcelamento="Mensal",
            numero_parcelas=3,
            valor_parcela=100.00,
            status="Pendente",
            usuario_cadastro=1
        )
        
        db.session.add(venda1)
        db.session.flush()  # Para pegar o ID
        
        # Adicionar item da venda
        item1 = ItemVenda(
            venda_id=venda1.id,
            produto_id=produto1.id,
            quantidade=2,
            preco_unitario=150.00,
            desconto=0,
            subtotal=300.00
        )
        db.session.add(item1)
        
        # Criar contas a receber (3 parcelas)
        data_base = datetime.now()
        for i in range(1, 4):
            data_vencimento = data_base + timedelta(days=30*i)
            conta = ContaReceber(
                venda_id=venda1.id,
                cliente_id=cliente1.id,
                vendedor_id=vendedor1.id,
                numero_parcela=i,
                data_vencimento=data_vencimento,
                valor_parcela=100.00,
                status="Pendente",
                usuario_cadastro=1
            )
            db.session.add(conta)
        
        # Venda 2 - Parcelada (2x)
        if len(clientes) > 1 and len(vendedores) > 1:
            cliente2 = clientes[1]
            vendedor2 = vendedores[1]
            produto2 = produtos[1] if len(produtos) > 1 else produto1
            
            venda2 = Venda(
                numero_venda="2",
                cliente_id=cliente2.id,
                vendedor_id=vendedor2.id,
                data_venda=datetime.now(),
                subtotal=200.00,
                desconto=20.00,
                total=180.00,
                forma_pagamento="Cartão",
                tipo_parcelamento="Semanal",
                numero_parcelas=2,
                valor_parcela=90.00,
                status="Pendente",
                usuario_cadastro=1
            )
            
            db.session.add(venda2)
            db.session.flush()
            
            # Adicionar item da venda
            item2 = ItemVenda(
                venda_id=venda2.id,
                produto_id=produto2.id,
                quantidade=1,
                preco_unitario=200.00,
                desconto=20.00,
                subtotal=180.00
            )
            db.session.add(item2)
            
            # Criar contas a receber (2 parcelas)
            for i in range(1, 3):
                data_vencimento = data_base + timedelta(weeks=i)
                conta = ContaReceber(
                    venda_id=venda2.id,
                    cliente_id=cliente2.id,
                    vendedor_id=vendedor2.id,
                    numero_parcela=i,
                    data_vencimento=data_vencimento,
                    valor_parcela=90.00,
                    status="Pendente",
                    usuario_cadastro=1
                )
                db.session.add(conta)
        
        try:
            db.session.commit()
            print("✅ Vendas de teste criadas com sucesso!")
            print(f"   Venda 1: R$ 300,00 (3x R$ 100,00)")
            print(f"   Venda 2: R$ 180,00 (2x R$ 90,00)")
            print(f"   Total de parcelas criadas: 5")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao criar vendas: {e}")

def main():
    """Função principal"""
    print("=== CRIANDO VENDAS DE TESTE ===\n")
    
    criar_vendas_teste()
    
    print("\n=== PRÓXIMOS PASSOS ===")
    print("1. Acesse: http://localhost:5000/contas-receber")
    print("2. Você deve ver as parcelas criadas")
    print("3. Clique em 'Pagar' em uma parcela")
    print("4. Após pagar, os botões de recibo devem aparecer")

if __name__ == "__main__":
    main() 