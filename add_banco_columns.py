#!/usr/bin/env python
"""Script para adicionar colunas de banco ao banco de dados existente."""

import sqlite3
import os
from datetime import datetime

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'webcosmeticos.db')

def add_banco_columns():
    """Adiciona colunas banco_id às tabelas ContaPagar e ContaReceber."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se as colunas já existem
        cursor.execute("PRAGMA table_info(conta_pagar)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'banco_id' not in columns:
            print("Adicionando coluna banco_id na tabela conta_pagar...")
            cursor.execute("ALTER TABLE conta_pagar ADD COLUMN banco_id INTEGER")
            conn.commit()
            print("✓ Coluna banco_id adicionada à tabela conta_pagar")
        else:
            print("✓ Coluna banco_id já existe na tabela conta_pagar")
        
        # Verificar se as colunas já existem em conta_receber
        cursor.execute("PRAGMA table_info(conta_receber)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'banco_id' not in columns:
            print("Adicionando coluna banco_id na tabela conta_receber...")
            cursor.execute("ALTER TABLE conta_receber ADD COLUMN banco_id INTEGER")
            conn.commit()
            print("✓ Coluna banco_id adicionada à tabela conta_receber")
        else:
            print("✓ Coluna banco_id já existe na tabela conta_receber")
        
        conn.close()
        print("\n✓ Banco de dados atualizado com sucesso!")
        return True
        
    except Exception as e:
        print(f"✗ Erro ao atualizar banco de dados: {e}")
        return False

if __name__ == '__main__':
    add_banco_columns()
