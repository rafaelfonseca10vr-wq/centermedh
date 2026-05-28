import sqlite3

conn = sqlite3.connect('instance/webcosmeticos.db')
cursor = conn.cursor()

# Lista de tabelas que precisam da coluna empresa_id
tables = [
    'cliente',
    'vendedor',
    'grupo_produto',
    'produto',
    'venda',
    'conta_receber'
]

# Adicionar coluna empresa_id a cada tabela se não existir
for table in tables:
    try:
        cursor.execute(f'ALTER TABLE {table} ADD COLUMN empresa_id INTEGER')
        print(f'Coluna empresa_id adicionada à tabela {table}')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print(f'Coluna empresa_id já existe na tabela {table}')
        else:
            print(f'Erro na tabela {table}: {e}')

# Pegar o ID da empresa padrão (deve ser 2)
cursor.execute('SELECT id FROM empresa WHERE nome = "Empresa Padrão"')
result = cursor.fetchone()
if result:
    empresa_id = result[0]
    print(f'Usando empresa_id: {empresa_id}')
    
    # Atualizar todos os registros com o empresa_id
    for table in tables:
        try:
            cursor.execute(f'UPDATE {table} SET empresa_id = ? WHERE empresa_id IS NULL', (empresa_id,))
            updated = cursor.rowcount
            print(f'{updated} registros atualizados na tabela {table}')
        except sqlite3.OperationalError as e:
            print(f'Erro ao atualizar tabela {table}: {e}')
else:
    print('Empresa padrão não encontrada!')

conn.commit()
conn.close()
print('Concluído!')
