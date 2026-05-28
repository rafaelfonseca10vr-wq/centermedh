#!/usr/bin/env python3
"""
Script para verificar o status das parcelas no banco de dados
"""

import sqlite3
import os
from datetime import datetime

def verificar_parcelas():
    """Verifica o status das parcelas no banco"""
    db_path = 'instance/webcosmeticos.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== VERIFICANDO PARCELAS NO BANCO ===\n")
    
    # Verificar todas as contas a receber
    cursor.execute("""
        SELECT 
            cr.id,
            cr.venda_id,
            cr.cliente_id,
            cr.numero_parcela,
            cr.data_vencimento,
            cr.valor_parcela,
            cr.valor_pago,
            cr.data_pagamento,
            cr.status,
            c.nome as cliente_nome,
            v.numero_venda
        FROM contas_receber cr
        LEFT JOIN cliente c ON cr.cliente_id = c.id
        LEFT JOIN venda v ON cr.venda_id = v.id
        ORDER BY cr.id
    """)
    
    parcelas = cursor.fetchall()
    
    if not parcelas:
        print("❌ Nenhuma parcela encontrada no banco!")
        return
    
    print(f"✅ Encontradas {len(parcelas)} parcelas:")
    print("\n" + "="*80)
    print(f"{'ID':<4} {'Venda':<8} {'Cliente':<20} {'Parcela':<8} {'Status':<10} {'Valor':<10} {'Pago':<10} {'Data Pagamento'}")
    print("="*80)
    
    parcelas_pagas = 0
    parcelas_pendentes = 0
    
    for parcela in parcelas:
        id_parcela, venda_id, cliente_id, num_parcela, data_venc, valor_parc, valor_pago, data_pag, status, cliente_nome, numero_venda = parcela
        
        # Formatar valores
        valor_parcela = float(valor_parc) if valor_parc else 0
        valor_pago = float(valor_pago) if valor_pago else 0
        data_pagamento = data_pag if data_pag else "N/A"
        
        # Contar por status
        if status == 'Pago':
            parcelas_pagas += 1
        else:
            parcelas_pendentes += 1
        
        print(f"{id_parcela:<4} {numero_venda:<8} {cliente_nome[:18]:<20} {num_parcela:<8} {status:<10} R${valor_parcela:<8.2f} R${valor_pago:<8.2f} {data_pagamento}")
    
    print("="*80)
    print(f"\n📊 RESUMO:")
    print(f"   Parcelas Pagas: {parcelas_pagas}")
    print(f"   Parcelas Pendentes: {parcelas_pendentes}")
    print(f"   Total: {len(parcelas)}")
    
    # Verificar parcelas pagas que devem ter botões de recibo
    if parcelas_pagas > 0:
        print(f"\n✅ Parcelas pagas encontradas! Você deve ver os botões de recibo para:")
        for parcela in parcelas:
            if parcela[8] == 'Pago':  # status
                print(f"   - Parcela ID {parcela[0]} (Venda {parcela[10]})")
    
    conn.close()

def testar_pagamento():
    """Testa o processo de pagamento"""
    print("\n=== TESTE DE PAGAMENTO ===")
    print("1. Acesse: http://localhost:5000/contas-receber")
    print("2. Clique no botão 'Pagar' em uma parcela pendente")
    print("3. Confirme o valor e clique em 'Confirmar Pagamento'")
    print("4. Após o pagamento, você deve ver:")
    print("   - Mensagem de sucesso")
    print("   - Botões 'Recibo' e 'Imprimir' aparecem")
    print("   - Status muda para 'Pago'")

def main():
    """Função principal"""
    print("=== VERIFICAÇÃO DE PARCELAS ===\n")
    
    verificar_parcelas()
    testar_pagamento()
    
    print("\n=== INSTRUÇÕES ===")
    print("Se você não vê os botões de recibo após pagar:")
    print("1. Recarregue a página (F5)")
    print("2. Verifique se a mensagem de sucesso apareceu")
    print("3. Procure por parcelas com status 'Pago'")
    print("4. Os botões devem aparecer apenas para parcelas pagas")

if __name__ == "__main__":
    main() 