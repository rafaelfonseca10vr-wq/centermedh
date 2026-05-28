#!/usr/bin/env python3
"""
Script para redefinir todos os usuários e criar um novo usuário master
"""

from app import app, db
from werkzeug.security import generate_password_hash
import sqlite3

def reset_users():
    # Usar SQL direto para evitar problemas com o ORM
    db_path = 'instance/webcosmeticos.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Excluir todos os usuários existentes
    cursor.execute('DELETE FROM user')
    conn.commit()
    print("Todos os usuários foram excluídos!")
    
    # Criar novo usuário master
    password_hash = generate_password_hash('Brasmid@2023')
    cursor.execute('''
        INSERT INTO user (username, email, password_hash, nome_completo, data_cadastro, ativo, admin)
        VALUES (?, ?, ?, ?, datetime('now'), 1, 1)
    ''', ('vitor', 'vitor@webcosmeticos.com', password_hash, 'Vitor'))
    conn.commit()
    
    conn.close()
    
    print("Novo usuário master criado com sucesso!")
    print("Username: vitor")
    print("Senha: Brasmid@2023")
    print("IMPORTANTE: Altere a senha após o primeiro login!")

if __name__ == '__main__':
    reset_users()
