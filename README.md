# CENTERMEDH WEB SYSTEM

Sistema web para venda de medicamentos desenvolvido em Python com Flask.

## Funcionalidades

- ✅ Sistema de login e autenticação
- ✅ Cadastro de usuários
- ✅ Dashboard responsivo
- 🔄 Sistema de permissões (em desenvolvimento)
- 🔄 Gestão de produtos (em desenvolvimento)
- 🔄 Sistema de vendas (em desenvolvimento)

## Instalação

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd webcosmeticos
```

2. **Crie um ambiente virtual:**
```bash
python -m venv venv
```

3. **Ative o ambiente virtual:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

5. **Execute a aplicação:**
```bash
python app.py
```

6. **Acesse no navegador:**
```
http://localhost:5000
```

## Estrutura do Projeto

```
webcosmeticos/
├── app.py                 # Aplicação principal Flask
├── requirements.txt       # Dependências Python
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── login.html        # Tela de login
│   ├── cadastro.html     # Tela de cadastro
│   └── dashboard.html    # Dashboard principal
└── webcosmeticos.db     # Banco de dados SQLite (criado automaticamente)
```

## Funcionalidades Implementadas

### Sistema de Autenticação
- Login com usuário e senha
- Cadastro de novos usuários
- Validação de dados
- Logout seguro

### Dashboard
- Interface moderna com tema verde
- Informações do usuário logado
- Cards para futuras funcionalidades
- Menu de navegação responsivo

### Banco de Dados
- Modelo de usuário com campos:
  - ID, username, email, senha (hash)
  - Nome completo, data de cadastro
  - Status ativo/inativo, permissão de admin

## Próximos Passos

1. **Sistema de Permissões**
   - Implementar roles e permissões por usuário
   - Interface de administração de usuários

2. **Gestão de Produtos**
   - CRUD de produtos cosméticos
   - Categorias e marcas
   - Controle de estoque

3. **Sistema de Vendas**
   - Carrinho de compras
   - Processamento de pedidos
   - Histórico de vendas

4. **Relatórios**
   - Estatísticas de vendas
   - Relatórios de produtos
   - Dashboard administrativo

## Tecnologias Utilizadas

- **Backend:** Python, Flask, SQLAlchemy
- **Frontend:** HTML5, CSS3, Bootstrap 5, Font Awesome
- **Banco de Dados:** SQLite
- **Autenticação:** Flask-Login

## Desenvolvimento

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Teste localmente
5. Envie um pull request

## Licença

Este projeto está sob a licença MIT. 