#!/usr/bin/env python3
"""
Script para atualizar a estrutura do banco de dados
"""

import sqlite3
import os

def verificar_estrutura_banco():
    """Verifica a estrutura atual do banco de dados"""
    db_path = 'instance/webcosmeticos.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar estrutura da tabela venda
    cursor.execute("PRAGMA table_info(venda)")
    colunas = cursor.fetchall()
    
    print("=== ESTRUTURA ATUAL DA TABELA VENDA ===")
    for coluna in colunas:
        print(f"  {coluna[1]} ({coluna[2]})")
    
    # Verificar colunas que devem existir
    colunas_necessarias = [
        'forma_pagamento',
        'tipo_parcelamento', 
        'numero_parcelas',
        'valor_parcela'
    ]
    
    colunas_existentes = [coluna[1] for coluna in colunas]
    
    print("\n=== COLUNAS FALTANDO ===")
    colunas_faltando = []
    for coluna in colunas_necessarias:
        if coluna not in colunas_existentes:
            print(f"  ❌ {coluna}")
            colunas_faltando.append(coluna)
        else:
            print(f"  ✅ {coluna}")
    
    conn.close()
    return colunas_faltando

def adicionar_colunas():
    """Adiciona as colunas que estão faltando"""
    db_path = 'instance/webcosmeticos.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Colunas para adicionar
    colunas_para_adicionar = [
        ('forma_pagamento', 'TEXT'),
        ('tipo_parcelamento', 'TEXT'),
        ('numero_parcelas', 'INTEGER'),
        ('valor_parcela', 'REAL')
    ]
    
    print("=== ADICIONANDO COLUNAS ===")
    
    for nome_coluna, tipo in colunas_para_adicionar:
        try:
            # Verificar se a coluna já existe
            cursor.execute(f"PRAGMA table_info(venda)")
            colunas = cursor.fetchall()
            colunas_existentes = [coluna[1] for coluna in colunas]
            
            if nome_coluna not in colunas_existentes:
                cursor.execute(f"ALTER TABLE venda ADD COLUMN {nome_coluna} {tipo}")
                print(f"  ✅ Adicionada coluna: {nome_coluna} ({tipo})")
            else:
                print(f"  ⚠️ Coluna já existe: {nome_coluna}")
                
        except Exception as e:
            print(f"  ❌ Erro ao adicionar {nome_coluna}: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Atualização concluída!")

def verificar_tabela_contas_receber():
    """Verifica se a tabela contas_receber existe"""
    db_path = 'instance/webcosmeticos.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar se a tabela existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contas_receber'")
    tabela_existe = cursor.fetchone() is not None
    
    if tabela_existe:
        print("✅ Tabela contas_receber existe")
        cursor.execute("PRAGMA table_info(contas_receber)")
        colunas = cursor.fetchall()
        print("Colunas da tabela contas_receber:")
        for coluna in colunas:
            print(f"  {coluna[1]} ({coluna[2]})")
    else:
        print("❌ Tabela contas_receber não existe")
    
    conn.close()
    return tabela_existe

def criar_tabela_contas_receber():
    """Cria a tabela contas_receber se não existir"""
    db_path = 'instance/webcosmeticos.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # SQL para criar a tabela
    sql = """
    CREATE TABLE IF NOT EXISTS contas_receber (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venda_id INTEGER NOT NULL,
        cliente_id INTEGER NOT NULL,
        vendedor_id INTEGER NOT NULL,
        numero_parcela INTEGER NOT NULL,
        data_vencimento DATE NOT NULL,
        valor_parcela REAL NOT NULL,
        valor_pago REAL DEFAULT 0,
        data_pagamento DATETIME,
        status TEXT DEFAULT 'Pendente',
        FOREIGN KEY (venda_id) REFERENCES venda (id),
        FOREIGN KEY (cliente_id) REFERENCES cliente (id),
        FOREIGN KEY (vendedor_id) REFERENCES vendedor (id)
    )
    """
    
    try:
        cursor.execute(sql)
        conn.commit()
        print("✅ Tabela contas_receber criada com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        return False
    finally:
        conn.close()

def main():
    """Função principal"""
    print("=== ATUALIZAÇÃO DO BANCO DE DADOS ===\n")
    
    # Verificar estrutura atual
    colunas_faltando = verificar_estrutura_banco()
    
    # Adicionar colunas se necessário
    if colunas_faltando:
        print(f"\nAdicionando {len(colunas_faltando)} colunas...")
        adicionar_colunas()
    else:
        print("\n✅ Todas as colunas necessárias já existem!")
    
    # Verificar tabela contas_receber
    print("\n=== VERIFICANDO TABELA CONTAS_RECEBER ===")
    if not verificar_tabela_contas_receber():
        print("Criando tabela contas_receber...")
        criar_tabela_contas_receber()
    
    print("\n=== VERIFICAÇÃO FINAL ===")
    verificar_estrutura_banco()
    
    print("\n✅ Atualização do banco concluída!")

if __name__ == "__main__":
    main() 