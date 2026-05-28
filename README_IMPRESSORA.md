# Configuração da Impressora Bluetooth Coojprt

## Visão Geral

O sistema agora suporta impressão de recibos na impressora Bluetooth Coojprt. Quando uma parcela é paga, o sistema pode gerar e imprimir automaticamente um recibo.

## Funcionalidades

- ✅ Geração automática de recibo ao pagar parcela
- ✅ Visualização do recibo no navegador
- ✅ Impressão via Bluetooth na Coojprt
- ✅ Descoberta automática de impressoras
- ✅ Formatação específica para recibos

## Instalação

### 1. Instalar Dependências

Execute o script de configuração:

```bash
python setup_impressora.py
```

Ou instale manualmente:

```bash
pip install PyBluez==0.23 python-escpos==3.0a8
```

### 2. Configurar Bluetooth (Windows)

1. **Habilitar Bluetooth:**
   - Configurações > Dispositivos > Bluetooth e outros dispositivos
   - Ativar Bluetooth

2. **Emparelhar Impressora:**
   - Ligar a impressora Coojprt
   - Pressionar botão de emparelhamento (se houver)
   - Adicionar dispositivo Bluetooth no Windows
   - Selecionar a impressora Coojprt

3. **Verificar Conexão:**
   - A impressora deve aparecer como "Conectado" nas configurações

### 3. Testar Configuração

Execute o teste da impressora:

```bash
python config_impressora.py
```

## Como Usar

### 1. Pagar Parcela

1. Acesse **Contas a Receber**
2. Clique no botão verde ✓ para pagar uma parcela
3. Confirme o valor e clique em **Pagar**
4. O recibo será gerado automaticamente

### 2. Visualizar Recibo

1. Para parcelas pagas, clique no botão 📄 (Visualizar Recibo)
2. O recibo abrirá em nova aba do navegador
3. Use Ctrl+P para imprimir via navegador

### 3. Imprimir via Bluetooth

1. Para parcelas pagas, clique no botão 🖨️ (Imprimir via Bluetooth)
2. Confirme a impressão
3. O recibo será enviado diretamente para a impressora Coojprt

## Estrutura do Recibo

```
========================================
         RECIBO DE PAGAMENTO
========================================

Data: 01/01/2024 10:00
Recibo Nº: 000001

========================================
CLIENTE:
Nome: João Silva
CPF: 123.456.789-00

VENDA:
Número: 1
Parcela: 1/3

========================================
VALOR PAGO: R$ 100.00
========================================

Vendedor: Maria Santos

========================================
Assinatura: _________________
========================================
```

## Solução de Problemas

### Erro: "Nenhuma impressora Coojprt encontrada"

**Possíveis causas:**
- Impressora desligada
- Bluetooth desabilitado
- Impressora não emparelhada
- Drivers não instalados

**Soluções:**
1. Verificar se a impressora está ligada
2. Habilitar Bluetooth no Windows
3. Emparelhar a impressora manualmente
4. Instalar drivers da Coojprt

### Erro: "Falha ao conectar com a impressora"

**Possíveis causas:**
- Impressora não está no modo de recepção
- Endereço MAC incorreto
- Porta Bluetooth ocupada

**Soluções:**
1. Verificar se a impressora está pronta para receber dados
2. Reiniciar a impressora
3. Verificar se não há outros programas usando a porta

### Erro: "Biblioteca Bluetooth não instalada"

**Solução:**
```bash
pip install PyBluez==0.23
```

**No Windows, pode ser necessário:**
```bash
pip install git+https://github.com/pybluez/pybluez.git
```

## Configuração Avançada

### Endereço MAC Fixo

Se quiser usar um endereço MAC específico, edite `config_impressora.py`:

```python
class ImpressoraCoojprt:
    def __init__(self, mac_address="00:11:22:33:44:55"):  # Seu MAC aqui
        self.mac_address = mac_address
```

### Comandos de Formatação

Para personalizar a formatação, edite os comandos em `config_impressora.py`:

```python
comandos = [
    b'\x1B\x40',      # Initialize printer
    b'\x1B\x61\x01',  # Center alignment
    b'\x1B\x21\x10',  # Double height and width
    # Adicione mais comandos conforme necessário
]
```

## Logs e Debug

Para ver logs detalhados, execute:

```bash
python -c "from config_impressora import testar_impressora; testar_impressora()"
```

## Suporte

Se encontrar problemas:

1. Verifique se a impressora está funcionando com outros programas
2. Teste a conexão Bluetooth com outros dispositivos
3. Consulte o manual da impressora Coojprt
4. Verifique se o Windows reconhece a impressora como dispositivo Bluetooth 