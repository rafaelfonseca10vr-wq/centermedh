#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para adicionar coluna tipo_conta à tabela conta_receber
Executa: python add_tipo_conta_receber.py
"""

import sqlite3
import os

def adicionar_coluna_tipo_conta():
    # Caminho do banco de dados
    db_path = os.path.join('instance', 'webcosmeticos.db')
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado em:", db_path)
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe em conta_receber
        cursor.execute("PRAGMA table_info(conta_receber)")
        colunas = cursor.fetchall()
        
        coluna_existe = any(col[1] == 'tipo_conta' for col in colunas)
        
        if not coluna_existe:
            print("Adicionando coluna tipo_conta na tabela conta_receber...")
            cursor.execute("ALTER TABLE conta_receber ADD COLUMN tipo_conta VARCHAR(20) DEFAULT 'Venda'")
            conn.commit()
            print("✓ Coluna tipo_conta adicionada à tabela conta_receber com sucesso!")
        else:
            print("✓ Coluna tipo_conta já existe na tabela conta_receber")
        
        # Fechar conexão
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {str(e)}")
        return False

def adicionar_coluna_vendedor_nullable():
    # Caminho do banco de dados
    db_path = os.path.join('instance', 'webcosmeticos.db')
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado em:", db_path)
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a coluna venda_id é nullable
        cursor.execute("PRAGMA table_info(conta_receber)")
        colunas = cursor.fetchall()
        
        venda_col = next((col for col in colunas if col[1] == 'venda_id'), None)
        vendedor_col = next((col for col in colunas if col[1] == 'vendedor_id'), None)
        
        if venda_col and not venda_col[3]:  # Se notnull = 0, então é nullable
            print("✓ Coluna venda_id já é nullable")
        else:
            print("⚠ Aviso: Coluna venda_id pode não ser nullable")
            print("  (A aplicação irá criar novos bancos de dados com as colunas corretas)")
        
        if vendedor_col and not vendedor_col[3]:  # Se notnull = 0, então é nullable
            print("✓ Coluna vendedor_id já é nullable")
        else:
            print("⚠ Aviso: Coluna vendedor_id pode não ser nullable")
            print("  (A aplicação irá criar novos bancos de dados com as colunas corretas)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar colunas: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Adicionando suporte para Contas Avulsas")
    print("=" * 50)
    
    sucesso1 = adicionar_coluna_tipo_conta()
    sucesso2 = adicionar_coluna_vendedor_nullable()
    
    if sucesso1 and sucesso2:
        print("\n✓ Migração concluída com sucesso!")
    else:
        print("\n❌ Houve problemas na migração")
