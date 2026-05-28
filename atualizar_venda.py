import sqlite3

conn = sqlite3.connect('instance/webcosmeticos.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE venda ADD COLUMN tipo_pagamento VARCHAR(20) DEFAULT "A Vista"')
    print('Campo tipo_pagamento adicionado')
except Exception as e:
    print(f'Erro ao adicionar tipo_pagamento: {e}')

try:
    cursor.execute('ALTER TABLE venda ADD COLUMN dias_entre_parcelas INTEGER DEFAULT 30')
    print('Campo dias_entre_parcelas adicionado')
except Exception as e:
    print(f'Erro ao adicionar dias_entre_parcelas: {e}')

conn.commit()
conn.close()
print('Atualização concluída')
