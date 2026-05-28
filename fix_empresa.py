import sqlite3

conn = sqlite3.connect('instance/webcosmeticos.db')
cursor = conn.cursor()

# Criar empresa padrão
cursor.execute('INSERT INTO empresa (nome, data_cadastro) VALUES (?, datetime("now"))', ('Empresa Padrão',))
empresa_id = cursor.lastrowid
print(f'Empresa criada com ID {empresa_id}')

# Atualizar usuário com o empresa_id
cursor.execute('UPDATE user SET empresa_id = ? WHERE username = ?', (empresa_id, 'vitor'))
conn.commit()
print('Usuário atualizado com empresa_id')

conn.close()
print('Concluído!')
