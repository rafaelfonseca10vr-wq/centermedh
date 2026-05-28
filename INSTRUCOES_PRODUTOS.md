# Sistema de Produtos - CENTERMEDH WEB SYSTEM

## Funcionalidades Implementadas

### ✅ Cadastro de Grupos de Produtos
- **Interface otimizada para mobile** com design responsivo
- **Nome do grupo** (obrigatório)
- **Descrição** (opcional)
- **Status ativo/inativo**
- **Exemplos de grupos** sugeridos na tela

### ✅ Cadastro de Produtos
- **Código único** do produto (obrigatório)
- **Nome do produto** (obrigatório)
- **Grupo** (obrigatório - deve ser criado primeiro)
- **Marca** (opcional)
- **Descrição** (opcional)
- **Preço de custo** (opcional)
- **Preço de venda** (obrigatório)
- **Estoque atual** (padrão: 0)
- **Estoque mínimo** (padrão: 0)
- **Status ativo/inativo**

### ✅ Listagem e Controle
- **Listagem de grupos** com contagem de produtos
- **Listagem de produtos** organizada por grupo
- **Indicadores visuais** de estoque (verde/amarelo/vermelho)
- **Preços formatados** em reais
- **Status ativo/inativo** com badges coloridos

## Como Usar

### 1. Criar Grupos de Produtos
1. Acesse o dashboard
2. Clique em "Ver Grupos"
3. Clique em "Novo Grupo"
4. Preencha:
   - **Nome**: Ex: "Coloração", "Progressiva", "Hidratação"
   - **Descrição**: Descrição opcional do grupo
   - **Ativo**: Checkbox para ativar/desativar

### 2. Cadastrar Produtos
1. Acesse "Ver Produtos" no dashboard
2. Clique em "Novo Produto"
3. Preencha os dados:
   - **Código**: Código único (Ex: COL001, PROG002)
   - **Nome**: Nome completo do produto
   - **Grupo**: Selecione um grupo criado
   - **Marca**: Marca do produto (opcional)
   - **Descrição**: Descrição detalhada (opcional)
   - **Preço de Custo**: Preço de compra (opcional)
   - **Preço de Venda**: Preço de venda (obrigatório)
   - **Estoque Atual**: Quantidade em estoque
   - **Estoque Mínimo**: Quantidade mínima para alerta
   - **Ativo**: Checkbox para ativar/desativar

## Exemplos de Grupos Sugeridos

### Grupos Principais:
- **Coloração**: Tintas, oxidantes, reveladores
- **Progressiva**: Produtos para alisamento
- **Hidratação**: Máscaras, condicionadores hidratantes
- **Shampoo**: Shampoos de diferentes tipos
- **Condicionador**: Condicionadores diversos
- **Máscara**: Máscaras de tratamento
- **Finalizador**: Produtos para finalização
- **Tratamento**: Produtos específicos para tratamentos

## Controle de Estoque

### Indicadores Visuais:
- 🟢 **Verde**: Estoque normal (acima do mínimo)
- 🟡 **Amarelo**: Estoque baixo (igual ou abaixo do mínimo)
- 🔴 **Vermelho**: Estoque zerado

### Funcionalidades:
- **Estoque atual**: Quantidade disponível
- **Estoque mínimo**: Alerta quando estoque baixa
- **Controle automático**: Indicadores visuais na listagem

## Validações Implementadas

### Grupos:
- Nome obrigatório
- Nome único (não permite duplicatas)
- Status ativo/inativo

### Produtos:
- Código obrigatório e único
- Nome obrigatório
- Grupo obrigatório
- Preço de venda obrigatório
- Preço de venda não pode ser menor que custo
- Valores numéricos validados

## Estrutura do Banco de Dados

### Tabela: grupo_produto
- id (Primary Key)
- nome (String, obrigatório)
- descricao (Text, opcional)
- ativo (Boolean, padrão: true)
- data_cadastro (DateTime)
- usuario_cadastro (Foreign Key)

### Tabela: produto
- id (Primary Key)
- codigo (String, único, obrigatório)
- nome (String, obrigatório)
- descricao (Text, opcional)
- marca (String, opcional)
- preco_custo (Numeric, opcional)
- preco_venda (Numeric, obrigatório)
- estoque (Integer, padrão: 0)
- estoque_minimo (Integer, padrão: 0)
- grupo_id (Foreign Key, obrigatório)
- ativo (Boolean, padrão: true)
- data_cadastro (DateTime)
- usuario_cadastro (Foreign Key)

## Próximas Funcionalidades

- [ ] Edição de grupos e produtos
- [ ] Busca e filtros
- [ ] Controle de estoque (entrada/saída)
- [ ] Relatórios de produtos
- [ ] Importação/exportação
- [ ] Fotos dos produtos
- [ ] Códigos de barras
- [ ] Alertas de estoque baixo

## Tecnologias Utilizadas

- **Backend**: Python Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **JavaScript**: Validações e máscaras
- **Banco**: SQLite
- **Validações**: Server-side e client-side 