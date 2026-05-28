#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para tornar colunas venda_id e vendedor_id nullable em conta_receber
Executa: python fix_conta_receber_nullable.py
"""

import sqlite3
import os

def fazer_venda_vendedor_nullable():
    # Caminho do banco de dados
    db_path = os.path.join('instance', 'webcosmeticos.db')
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado em:", db_path)
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Verificando estrutura atual da tabela conta_receber...")
        cursor.execute("PRAGMA table_info(conta_receber)")
        colunas = cursor.fetchall()
        
        # Criar nova tabela com as colunas corretas
        print("Criando nova tabela com colunas corretas...")
        
        # Primeiro, salvar os dados existentes
        cursor.execute("SELECT * FROM conta_receber")
        dados = cursor.fetchall()
        
        # Renomear tabela antiga
        cursor.execute("ALTER TABLE conta_receber RENAME TO conta_receber_old")
        
        # Criar nova tabela com as colunas corretas
        cursor.execute("""
            CREATE TABLE conta_receber (
                id INTEGER PRIMARY KEY,
                venda_id INTEGER,
                cliente_id INTEGER NOT NULL,
                vendedor_id INTEGER,
                numero_parcela INTEGER NOT NULL,
                data_vencimento DATETIME NOT NULL,
                valor_parcela NUMERIC(10, 2) NOT NULL,
                valor_pago NUMERIC(10, 2) DEFAULT 0,
                data_pagamento DATETIME,
                banco_id INTEGER,
                status VARCHAR(20) DEFAULT 'Pendente',
                tipo_conta VARCHAR(20) DEFAULT 'Venda',
                observacoes TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                usuario_cadastro INTEGER,
                empresa_id INTEGER NOT NULL,
                FOREIGN KEY(venda_id) REFERENCES venda(id),
                FOREIGN KEY(cliente_id) REFERENCES cliente(id),
                FOREIGN KEY(vendedor_id) REFERENCES vendedor(id),
                FOREIGN KEY(banco_id) REFERENCES banco(id),
                FOREIGN KEY(usuario_cadastro) REFERENCES user(id),
                FOREIGN KEY(empresa_id) REFERENCES empresa(id)
            )
        """)
        
        # Copiar dados da tabela antiga
        if dados:
            print("Copiando dados da tabela antiga...")
            for linha in dados:
                cursor.execute("""
                    INSERT INTO conta_receber 
                    (id, venda_id, cliente_id, vendedor_id, numero_parcela, data_vencimento,
                     valor_parcela, valor_pago, data_pagamento, banco_id, status, tipo_conta,
                     observacoes, data_cadastro, usuario_cadastro, empresa_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, linha)
        
        # Remover tabela antiga
        cursor.execute("DROP TABLE conta_receber_old")
        
        conn.commit()
        print("✓ Tabela conta_receber atualizada com sucesso!")
        print("✓ Colunas venda_id e vendedor_id agora são nullable")
        print(f"✓ {len(dados)} registros preservados")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar tabela: {str(e)}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Tentar reverter se houve erro
            cursor.execute("DROP TABLE IF EXISTS conta_receber")
            cursor.execute("ALTER TABLE conta_receber_old RENAME TO conta_receber")
            conn.commit()
            conn.close()
        except:
            pass
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Corrigindo esquema da tabela conta_receber")
    print("=" * 60)
    
    sucesso = fazer_venda_vendedor_nullable()
    
    if sucesso:
        print("\n✓ Migração concluída com sucesso!")
    else:
        print("\n❌ Houve problemas na migração")
