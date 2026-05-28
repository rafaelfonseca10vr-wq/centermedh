# Cadastro de Clientes - CENTERMEDH WEB SYSTEM

## Funcionalidades Implementadas

### ✅ Tela de Cadastro de Clientes
- **Interface otimizada para mobile** com design responsivo
- **Campos obrigatórios**: CPF e Nome
- **Campos opcionais**: Email, Telefone, Endereço completo
- **Validação de CPF** automática
- **Máscaras automáticas** para CPF, telefone e CEP
- **Consulta automática de CEP** via API ViaCEP
- **Status ativo/inativo** do cliente

### ✅ Recursos Mobile-First
- Layout responsivo que funciona perfeitamente em celulares
- Campos grandes e fáceis de tocar
- Navegação intuitiva
- Botões bem posicionados para uso com polegar

### ✅ Validações Implementadas
- **CPF**: Validação completa com dígitos verificadores
- **CPF único**: Não permite CPFs duplicados
- **Formatação automática**: CPF, telefone e CEP
- **Campos obrigatórios**: Nome e CPF

### ✅ Consulta de CEP
- **API ViaCEP**: Consulta automática de endereço
- **Preenchimento automático**: Endereço, bairro, cidade e estado
- **Permite edição manual**: Após preenchimento automático
- **Botão de busca**: Para consultar CEP manualmente

## Como Usar

### 1. Acessar o Sistema
```
http://localhost:5000
```
Login: `admin` / Senha: `admin123`

### 2. Navegar para Clientes
- No dashboard, clique em "Ver Clientes"
- Ou acesse diretamente: `http://localhost:5000/clientes`

### 3. Cadastrar Novo Cliente
- Clique em "Novo Cliente"
- Preencha os dados:
  - **CPF** (obrigatório): Digite apenas números, será formatado automaticamente
  - **Nome** (obrigatório): Nome completo do cliente
  - **Email**: Opcional
  - **Telefone**: Opcional, será formatado automaticamente
  - **CEP**: Digite o CEP e clique em "Buscar" ou saia do campo
  - **Endereço**: Preenchido automaticamente pelo CEP
  - **Número**: Número da casa/apartamento
  - **Bairro**: Preenchido automaticamente pelo CEP
  - **Cidade**: Preenchido automaticamente pelo CEP
  - **Estado**: Preenchido automaticamente pelo CEP
  - **Cliente Ativo**: Checkbox para ativar/desativar

### 4. Funcionalidades da Tela
- **Máscaras automáticas**: CPF, telefone e CEP formatados
- **Consulta CEP**: Preenche endereço automaticamente
- **Validação em tempo real**: CPF válido e único
- **Responsivo**: Funciona perfeitamente em celulares
- **Botões grandes**: Fáceis de tocar em telas pequenas

## Campos do Cliente

| Campo | Tipo | Obrigatório | Formatação |
|-------|------|-------------|------------|
| CPF | Texto | Sim | 000.000.000-00 |
| Nome | Texto | Sim | - |
| Email | Email | Não | - |
| Telefone | Texto | Não | (00) 00000-0000 |
| CEP | Texto | Não | 00000-000 |
| Endereço | Texto | Não | - |
| Número | Texto | Não | - |
| Bairro | Texto | Não | - |
| Cidade | Texto | Não | - |
| Estado | Select | Não | UF |
| Ativo | Checkbox | Não | Sim/Não |

## Próximas Funcionalidades

- [ ] Edição de clientes
- [ ] Visualização detalhada
- [ ] Busca e filtros
- [ ] Exportação de dados
- [ ] Histórico de alterações
- [ ] Foto do cliente
- [ ] Observações/notas

## Tecnologias Utilizadas

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **JavaScript**: Máscaras e validações
- **API**: ViaCEP para consulta de endereços
- **Banco**: SQLite com SQLAlchemy 