#!/usr/bin/env python3
"""
Script para criar um usuário administrador no sistema CENTERMEDH WEB SYSTEM
"""

from app import app, db, User
from werkzeug.security import generate_password_hash

def create_admin_user():
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
        
        # Verificar se já existe um admin
        admin = User.query.filter_by(admin=True).first()
        if admin:
            print(f"Usuário administrador já existe: {admin.username}")
            return
        
        # Criar usuário administrador
        admin_user = User(
            username='admin',
            email='admin@webcosmeticos.com',
            nome_completo='Administrador do Sistema',
            admin=True,
            ativo=True
        )
        admin_user.set_password('admin123')
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("Usuário administrador criado com sucesso!")
        print("Username: admin")
        print("Senha: admin123")
        print("IMPORTANTE: Altere a senha após o primeiro login!")

if __name__ == '__main__':
    create_admin_user() 