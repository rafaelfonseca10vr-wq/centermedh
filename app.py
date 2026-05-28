from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import re
from flask import jsonify, request
import io
import xml.etree.ElementTree as ET
try:
    from weasyprint import HTML
except Exception:
    HTML = None
from typing import cast
from sqlalchemy import func, and_

app = Flask(__name__, instance_relative_config=True)
os.makedirs(app.instance_path, exist_ok=True)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
db_path = os.path.join(app.instance_path, 'webcosmeticos.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path.replace(os.sep, '/')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = cast(str, 'login')

# Modelo de Empresa
class Empresa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    # Adicione outros campos se necessário

# Modelo de Usuário
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    nome_completo = db.Column(db.String(120), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    admin = db.Column(db.Boolean, default=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref='usuarios')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Modelo de Cliente
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(18), unique=True, nullable=True)
    nome = db.Column(db.String(120), nullable=False)
    nome_fantasia = db.Column(db.String(120))
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(15))
    cep = db.Column(db.String(9))
    endereco = db.Column(db.String(200))
    numero = db.Column(db.String(10))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    inscricao_estadual = db.Column(db.String(20))
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_cadastro = db.Column(db.Integer, db.ForeignKey('user.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref='clientes')

# Modelo de Vendedor
class Vendedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(15))
    comissao = db.Column(db.Numeric(5, 2), default=0)  # Percentual de comissão
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_cadastro = db.Column(db.Integer, db.ForeignKey('user.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref='vendedores')
    
    __table_args__ = (db.UniqueConstraint('cpf', 'empresa_id', name='unique_cpf_empresa'),)

# Modelo de Fornecedor
class Fornecedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cnpj = db.Column(db.String(18), nullable=False)
    razao_social = db.Column(db.String(120), nullable=False)
    nome_fantasia = db.Column(db.String(120))
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(15))
    cep = db.Column(db.String(9))
    endereco = db.Column(db.String(200))
    numero = db.Column(db.String(10))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    inscricao_estadual = db.Column(db.String(20))
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_cadastro = db.Column(db.Integer, db.ForeignKey('user.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref='fornecedores')
    
    __table_args__ = (db.UniqueConstraint('cnpj', 'empresa_id', name='unique_cnpj_empresa'),)

# Modelo de Grupo de Produtos
class GrupoProduto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_cadastro = db.Column(db.Integer, db.ForeignKey('user.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref='grupos')
    
    # Relacionamento com produtos
    produtos = db.relationship('Produto', backref='grupo', lazy=True)

# Modelo de Produto
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    codigo_fornecedor = db.Column(db.String(50))
    ncm = db.Column(db.String(20))
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    marca = db.Column(db.String(100))
    preco_custo = db.Column(db.Numeric(10, 2))
    preco_venda = db.Column(db.Numeric(10, 2), nullable=False)
    estoque = db.Column(db.Integer, default=0)
    estoque_minimo = db.Column(db.Integer, default=0)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo_produto.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_cadastro = db.Column(db.Integer, db.ForeignKey('user.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref='produtos')

# Modelo de Grade de Estoque
class GradeEstoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    lote = db.Column(db.String(100))
    data_vencimento = db.Column(db.DateTime)
    quantidade = db.Column(db.Integer, default=0)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedor.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_cadastro = db.Column(db.Integer, db.ForeignKey('user.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    produto = db.relationship('Produto', backref='grades_estoque')
    fornecedor = db.relationship('Fornecedor', backref='grades_estoque')
    empresa = db.relationship('Empresa')

# Modelo de Venda
class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_venda = db.Column(db.String(20), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedor.id'), nullable=False)
    data_venda = db.Column(db.DateTime, default=datetime.utcnow)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    desconto = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    forma_pagamento = db.Column(db.String(50))  # Dinheiro, PIX, Cartão, etc.
    tipo_pagamento = db.Column(db.String(20), default='A Vista')  # A Vista, A Prazo
    tipo_parcelamento = db.Column(db.String(20), default='A Vista')  # A Vista, Semanal, Mensal, Personalizado
    numero_parcelas = db.Column(db.Integer, default=1)  # Quantidade de parcelas
    dias_entre_parcelas = db.Column(db.Integer, default=30)  # Dias entre parcelas (30, 45, 60, etc)
    valor_parcela = db.Column(db.Numeric(10, 2))  # Valor de cada parcela
    status = db.Column(db.String(20), default='Pendente')  # Pendente, Pago, Cancelado
    observacoes = db.Column(db.Text)
    usuario_cadastro = db.Column(db.Integer, db.ForeignKey('user.id'))
    impresso = db.Column(db.Boolean, default=False)  # Controle de impressão
    excluido = db.Column(db.Boolean, default=False)  # Controle de exclusão
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref='vendas')
    
    # Relacionamentos
    cliente = db.relationship('Cliente', backref='vendas')
    vendedor = db.relationship('Vendedor', backref='vendas')
    itens = db.relationship('ItemVenda', backref='venda', cascade='all, delete-orphan')

# Modelo de Item da Venda
class ItemVenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey('venda.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    desconto = db.Column(db.Numeric(10, 2), default=0)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    brinde = db.Column(db.String(120))
    troca = db.Column(db.String(120))
    
    # Relacionamento
    produto = db.relationship('Produto')

# Modelo de Conta a Receber
class ContaReceber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey('venda.id'), nullable=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedor.id'), nullable=True)
    numero_parcela = db.Column(db.Integer, nullable=False, default=1)  # 1, 2, 3, etc.
    data_vencimento = db.Column(db.DateTime, nullable=False)
    valor_parcela = db.Column(db.Numeric(10, 2), nullable=False)
    valor_pago = db.Column(db.Numeric(10, 2), default=0)
    data_pagamento = db.Column(db.DateTime)
    banco_id = db.Column(db.Integer, db.ForeignKey('banco.id'), nullable=True)
    status = db.Column(db.String(20), default='Pendente')  # Pendente, Pago, Atrasado
    tipo_conta = db.Column(db.String(20), default='Venda')  # Venda ou Avulsa
    observacoes = db.Column(db.Text)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_cadastro = db.Column(db.Integer, db.ForeignKey('user.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref='contas_receber')
    
    # Relacionamentos
    venda = db.relationship('Venda', backref='contas_receber')
    cliente = db.relationship('Cliente')
    vendedor = db.relationship('Vendedor')
    banco = db.relationship('Banco', backref='contas_receber_pagas')

# Modelo de Conta a Pagar
class ContaPagar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedor.id'), nullable=False)
    numero_nota_fiscal = db.Column(db.String(20), nullable=False)
    data_entrada = db.Column(db.DateTime, nullable=False)
    data_vencimento = db.Column(db.DateTime, nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    valor_pago = db.Column(db.Numeric(10, 2), default=0)
    data_pagamento = db.Column(db.DateTime)
    banco_id = db.Column(db.Integer, db.ForeignKey('banco.id'), nullable=True)
    status = db.Column(db.String(20), default='Aberto')  # Aberto, Pago, Atrasado
    observacoes = db.Column(db.Text)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_cadastro = db.Column(db.Integer, db.ForeignKey('user.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref='contas_pagar')
    
    # Relacionamentos
    fornecedor = db.relationship('Fornecedor', backref='contas_pagar')
    banco = db.relationship('Banco', backref='contas_pagar_pagas')

# Modelo de Banco
class Banco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    numero_banco = db.Column(db.String(20), nullable=False)
    agencia = db.Column(db.String(20), nullable=False)
    conta = db.Column(db.String(30), nullable=False)
    tipo_conta = db.Column(db.String(20), default='Corrente')  # Corrente, Poupança
    saldo = db.Column(db.Numeric(15, 2), default=0)
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_cadastro = db.Column(db.Integer, db.ForeignKey('user.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref='bancos')
    
    __table_args__ = (db.UniqueConstraint('numero_banco', 'agencia', 'conta', 'empresa_id', name='unique_banco_empresa'),)

# Modelo de Movimentação Bancária
class MovimentacaoBancaria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    banco_id = db.Column(db.Integer, db.ForeignKey('banco.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # Entrada, Saída
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    saldo_anterior = db.Column(db.Numeric(15, 2), nullable=False)
    saldo_novo = db.Column(db.Numeric(15, 2), nullable=False)
    conta_pagar_id = db.Column(db.Integer, db.ForeignKey('conta_pagar.id'), nullable=True)
    conta_receber_id = db.Column(db.Integer, db.ForeignKey('conta_receber.id'), nullable=True)
    data_movimentacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    
    banco = db.relationship('Banco', backref='movimentacoes')
    usuario = db.relationship('User', backref='movimentacoes_bancarias')
    empresa = db.relationship('Empresa', backref='movimentacoes_bancarias')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Função para validar CPF
def validar_cpf(cpf):
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Calcula o segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    # Verifica se os dígitos calculados são iguais aos do CPF
    return cpf[-2:] == f"{digito1}{digito2}"

# Função para formatar CPF
def formatar_cpf(cpf):
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

# Função para formatar telefone
def formatar_telefone(telefone):
    telefone = re.sub(r'[^0-9]', '', telefone)
    if len(telefone) == 11:
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    return telefone

# Função para validar CNPJ
def validar_cnpj(cnpj):
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    def calcular_digito(base, pesos):
        soma = sum(int(base[i]) * pesos[i] for i in range(len(base)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito1 = calcular_digito(cnpj[:12], pesos1)
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito2 = calcular_digito(cnpj[:12] + str(digito1), pesos2)
    return cnpj[-2:] == f"{digito1}{digito2}"

# Função para formatar CNPJ
def formatar_cnpj(cnpj):
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj

# Função para converter valores numéricos brasileiros
def parse_decimal(valor):
    if valor is None:
        return 0

    texto = str(valor).strip()
    if texto == '':
        return 0

    # Remove espaços e símbolos de moeda
    texto = texto.replace(' ', '').replace('R$', '').replace('$', '')

    has_dot = '.' in texto
    has_comma = ',' in texto

    if has_dot and has_comma:
        # Formato brasileiro com separador de milhar e decimal: 1.234,56
        if texto.index('.') < texto.index(','):
            texto = texto.replace('.', '')
            texto = texto.replace(',', '.')
        else:
            # Caso contrário, provável formato americano com milhar em vírgula: 1,234.56
            texto = texto.replace(',', '')
    elif has_comma:
        texto = texto.replace(',', '.')

    try:
        return float(texto)
    except ValueError:
        return 0

# Função para converter datas de XML para datetime
def parse_date(valor):
    if not valor:
        return None
    formatos = ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S-03:00', '%Y-%m-%dT%H:%M:%S%z']
    for fmt in formatos:
        try:
            return datetime.strptime(valor, fmt)
        except ValueError:
            continue
    return None

# Helpers para encontrar elementos XML com ou sem namespace

def ns_path(path):
    if not path:
        return path
    prefix = ''
    if path.startswith('.//'):
        prefix = './/'
        path = path[3:]
    return prefix + '/'.join(
        f'{{*}}{segment}' if segment and not segment.startswith('{') else segment
        for segment in path.split('/')
    )


def xml_find(element, path):
    if element is None:
        return None
    found = element.find(path)
    if found is not None:
        return found
    return element.find(ns_path(path))


def xml_findtext(element, path):
    found = xml_find(element, path)
    if found is None or found.text is None:
        return None
    return found.text.strip()


def xml_findall(element, path):
    if element is None:
        return []
    found = element.findall(path)
    if found:
        return found
    return element.findall(ns_path(path))

# Função para localizar ou criar fornecedor pela NFe
def get_or_create_fornecedor(cnpj, empresa_id, emissores):
    cnpj_formatado = formatar_cnpj(cnpj)
    fornecedor = Fornecedor.query.filter_by(cnpj=cnpj_formatado, empresa_id=empresa_id).first()
    if fornecedor:
        return fornecedor

    fornecedor = Fornecedor(
        cnpj=cnpj_formatado,
        razao_social=emissores.get('razao_social') or emissores.get('xNome') or 'Fornecedor NFe',
        nome_fantasia=emissores.get('nome_fantasia') or emissores.get('xFant'),
        inscricao_estadual=emissores.get('inscricao_estadual') or emissores.get('IE'),
        email=emissores.get('email'),
        telefone=emissores.get('telefone'),
        cep=emissores.get('cep'),
        endereco=emissores.get('endereco'),
        numero=emissores.get('numero'),
        bairro=emissores.get('bairro'),
        cidade=emissores.get('cidade'),
        estado=emissores.get('estado'),
        ativo=True,
        usuario_cadastro=current_user.id,
        empresa_id=empresa_id
    )
    db.session.add(fornecedor)
    db.session.flush()
    return fornecedor

# Função para localizar ou criar produto pela NFe
def get_or_create_produto(codigo, nome, fornecedor_codigo, empresa_id, preco_custo=None, ncm=None):
    produto = Produto.query.filter_by(codigo=codigo, empresa_id=empresa_id).first()
    if produto:
        if fornecedor_codigo and not produto.codigo_fornecedor:
            produto.codigo_fornecedor = fornecedor_codigo
        if nome and not produto.nome:
            produto.nome = nome
        if preco_custo is not None and (produto.preco_custo is None or float(produto.preco_custo) == 0):
            produto.preco_custo = preco_custo
        if ncm and not produto.ncm:
            produto.ncm = ncm
        return produto

    grupo = GrupoProduto.query.filter_by(empresa_id=empresa_id).first()
    if not grupo:
        grupo = GrupoProduto(nome='Sem Grupo', empresa_id=empresa_id)
        db.session.add(grupo)
        db.session.flush()

    produto = Produto(
        codigo=codigo,
        codigo_fornecedor=fornecedor_codigo,
        ncm=ncm,
        nome=nome or f'Produto {codigo}',
        preco_custo=preco_custo if preco_custo is not None else 0,
        preco_venda=0,
        estoque=0,
        estoque_minimo=0,
        grupo_id=grupo.id,
        ativo=True,
        usuario_cadastro=current_user.id,
        empresa_id=empresa_id
    )
    db.session.add(produto)
    db.session.flush()
    return produto

# Função para atualizar grade de estoque por lote
def atualizar_grade_estoque(produto, fornecedor, lote, data_vencimento, quantidade):
    if not lote:
        lote = 'SEM_LOTE'

    grade = GradeEstoque.query.filter_by(
        produto_id=produto.id,
        lote=lote,
        fornecedor_id=fornecedor.id,
        empresa_id=current_user.empresa_id
    ).first()

    if grade:
        grade.quantidade += quantidade
        if data_vencimento:
            grade.data_vencimento = data_vencimento
    else:
        grade = GradeEstoque(
            produto_id=produto.id,
            lote=lote,
            data_vencimento=data_vencimento,
            quantidade=quantidade,
            fornecedor_id=fornecedor.id,
            usuario_cadastro=current_user.id,
            empresa_id=current_user.empresa_id
        )
        db.session.add(grade)

    produto.estoque = (produto.estoque or 0) + quantidade
    return grade

# Função para gerar número da venda
def gerar_numero_venda():
    # Buscar a última venda para pegar o próximo número sequencial
    ultima_venda = Venda.query.order_by(Venda.id.desc()).first()
    if ultima_venda:
        # Tentar extrair o número da última venda
        try:
            ultimo_numero = int(ultima_venda.numero_venda)
            return str(ultimo_numero + 1)
        except ValueError:
            # Se não conseguir converter, usar o ID da última venda + 1
            return str(ultima_venda.id + 1)
    else:
        # Primeira venda
        return "1"

# Rotas
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = None
        if username:
            normalized_username = username.lower()
            user = User.query.filter(func.lower(User.username) == normalized_username).first()
        
        if user and user.check_password(password):
            if user.ativo:
                login_user(user)
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Usuário inativo. Entre em contato com o administrador.', 'error')
        else:
            flash('Usuário ou senha incorretos.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        nome_completo = request.form.get('nome_completo')
        empresa_nome = request.form.get('empresa_nome')
        # Validações
        username_exists = User.query.filter(func.lower(User.username) == username.lower()).first() if username else None
        if username_exists:
            flash('Nome de usuário já existe.', 'error')
            return render_template('cadastro.html')
        email_exists = User.query.filter(func.lower(User.email) == email.lower()).first() if email else None
        if email_exists:
            flash('Email já cadastrado.', 'error')
            return render_template('cadastro.html')
        if password != confirm_password:
            flash('Senhas não coincidem.', 'error')
            return render_template('cadastro.html')
        if not password or len(password) < 6:
            flash('Senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('cadastro.html')
        if not empresa_nome:
            flash('Nome da empresa é obrigatório.', 'error')
            return render_template('cadastro.html')
        # Criar nova empresa
        empresa = Empresa(nome=empresa_nome)
        db.session.add(empresa)
        db.session.commit()
        # Criar novo usuário vinculado à empresa
        user = User(
            username=username,
            email=email,
            nome_completo=nome_completo,
            password_hash='',
            ativo=True,
            admin=True,
            empresa_id=empresa.id
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Rotas para Clientes
@app.route('/clientes')
@login_required
def clientes():
    if current_user.admin:
        lista = Cliente.query.filter_by(ativo=True).order_by(Cliente.nome).all()
    else:
        lista = Cliente.query.filter_by(ativo=True, usuario_cadastro=current_user.id).order_by(Cliente.nome).all()
    return render_template('clientes.html', clientes=lista)

@app.route('/clientes/novo', methods=['GET', 'POST'])
@login_required
def novo_cliente():
    if request.method == 'POST':
        cpf_cnpj = request.form.get('cpf_cnpj')
        inscricao_estadual = request.form.get('inscricao_estadual')
        nome = request.form.get('nome')
        nome_fantasia = request.form.get('nome_fantasia')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        cep = request.form.get('cep')
        endereco = request.form.get('endereco')
        numero = request.form.get('numero')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        ativo = request.form.get('ativo') == 'on'
        # Validações
        if cpf_cnpj:
            cpf_cnpj_limpo = re.sub(r'[^\d]', '', cpf_cnpj)
            if len(cpf_cnpj_limpo) == 11:
                if not validar_cpf(cpf_cnpj):
                    flash('CPF inválido.', 'error')
                    return render_template('novo_cliente.html')
            elif len(cpf_cnpj_limpo) == 14:
                # Validação básica de CNPJ
                pass
            else:
                flash('CPF/CNPJ inválido.', 'error')
                return render_template('novo_cliente.html')
            if Cliente.query.filter_by(cpf=cpf_cnpj, empresa_id=current_user.empresa_id).first():
                flash('CPF/CNPJ já cadastrado.', 'error')
                return render_template('novo_cliente.html')
        if not nome:
            flash('Nome é obrigatório.', 'error')
            return render_template('novo_cliente.html')
        # Criar novo cliente
        cliente = Cliente(
            cpf=cpf_cnpj if cpf_cnpj else None,
            nome=nome,
            nome_fantasia=nome_fantasia,
            email=email,
            telefone=formatar_telefone(telefone) if telefone else None,
            cep=cep,
            endereco=endereco,
            numero=numero,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            inscricao_estadual=inscricao_estadual,
            ativo=ativo,
            usuario_cadastro=current_user.id,
            empresa_id=current_user.empresa_id
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente cadastrado com sucesso!', 'success')
        return redirect(url_for('clientes'))
    return render_template('novo_cliente.html')

# Rotas para Fornecedores
@app.route('/fornecedores')
@login_required
def fornecedores():
    fornecedores = Fornecedor.query.filter_by(empresa_id=current_user.empresa_id).order_by(Fornecedor.razao_social).all()
    return render_template('fornecedores.html', fornecedores=fornecedores)

@app.route('/fornecedores/novo', methods=['GET', 'POST'])
@login_required
def novo_fornecedor():
    if request.method == 'POST':
        cnpj = request.form.get('cnpj')
        razao_social = request.form.get('razao_social')
        nome_fantasia = request.form.get('nome_fantasia')
        inscricao_estadual = request.form.get('inscricao_estadual')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        cep = request.form.get('cep')
        endereco = request.form.get('endereco')
        numero = request.form.get('numero')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        ativo = request.form.get('ativo') == 'on'

        if not cnpj:
            flash('CNPJ é obrigatório.', 'error')
            return render_template('novo_fornecedor.html')

        if not validar_cnpj(cnpj):
            flash('CNPJ inválido.', 'error')
            return render_template('novo_fornecedor.html')

        cnpj_formatado = formatar_cnpj(cnpj)
        if Fornecedor.query.filter_by(cnpj=cnpj_formatado, empresa_id=current_user.empresa_id).first():
            flash('CNPJ já cadastrado nesta empresa.', 'error')
            return render_template('novo_fornecedor.html')

        if not razao_social:
            flash('Razão social é obrigatória.', 'error')
            return render_template('novo_fornecedor.html')

        fornecedor = Fornecedor(
            cnpj=cnpj_formatado,
            razao_social=razao_social,
            nome_fantasia=nome_fantasia,
            inscricao_estadual=inscricao_estadual,
            email=email,
            telefone=formatar_telefone(telefone) if telefone else None,
            cep=cep,
            endereco=endereco,
            numero=numero,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            ativo=ativo,
            usuario_cadastro=current_user.id,
            empresa_id=current_user.empresa_id
        )
        db.session.add(fornecedor)
        db.session.commit()

        flash('Fornecedor cadastrado com sucesso!', 'success')
        return redirect(url_for('fornecedores'))

    return render_template('novo_fornecedor.html')

# Importação de NFe XML para estoque e contas a pagar
@app.route('/importar-nfe', methods=['GET', 'POST'])
@login_required
def importar_nfe():
    if request.method == 'POST':
        arquivo = request.files.get('arquivo')
        if not arquivo or arquivo.filename == '':
            flash('Selecione um arquivo XML.', 'error')
            return render_template('importar_nfe.html')

        try:
            tree = ET.parse(arquivo)
            root = tree.getroot()
        except ET.ParseError:
            flash('Arquivo XML inválido.', 'error')
            return render_template('importar_nfe.html')

        infNFe = xml_find(root, './/infNFe') or root
        emit = xml_find(infNFe, 'emit')
        if emit is None:
            flash('Emitente não encontrado no XML da NFe.', 'error')
            return render_template('importar_nfe.html')

        cnpj = xml_findtext(emit, 'CNPJ') or xml_findtext(emit, 'CPF')
        if not cnpj:
            flash('CNPJ do fornecedor não encontrado no XML.', 'error')
            return render_template('importar_nfe.html')

        emissores = {
            'razao_social': xml_findtext(emit, 'xNome'),
            'nome_fantasia': xml_findtext(emit, 'xFant'),
            'inscricao_estadual': xml_findtext(emit, 'IE'),
            'email': None,
            'telefone': None,
            'cep': None,
            'endereco': None,
            'numero': None,
            'bairro': None,
            'cidade': None,
            'estado': None
        }

        fornecedor = get_or_create_fornecedor(cnpj, current_user.empresa_id, emissores)

        numero_nota_fiscal = xml_findtext(infNFe, './/ide/nNF') or xml_findtext(infNFe, 'ide/nNF') or xml_findtext(infNFe, './/nNF') or '0'
        data_entrada = parse_date(xml_findtext(infNFe, './/ide/dEmi') or xml_findtext(infNFe, './/ide/dhEmi'))
        if not data_entrada:
            data_entrada = datetime.utcnow()

        data_vencimento = None
        dup = xml_find(infNFe, './/cobr/dup')
        if dup is not None:
            data_vencimento = parse_date(xml_findtext(dup, 'dVenc'))
        if not data_vencimento:
            data_vencimento = datetime.utcnow() + timedelta(days=30)

        total_nota = parse_decimal(xml_findtext(infNFe, './/ICMSTot/vNF') or xml_findtext(infNFe, './/total/ICMSTot/vNF'))
        itens = xml_findall(infNFe, './/det')
        if not itens:
            flash('Nenhum item encontrado no XML.', 'error')
            return render_template('importar_nfe.html')

        for det in itens:
            prod = xml_find(det, 'prod')
            if prod is None:
                continue

            codigo = xml_findtext(prod, 'cProd') or ''
            nome = xml_findtext(prod, 'xProd') or 'Produto sem descrição'
            lote = xml_findtext(prod, 'nLote') or 'SEM_LOTE'
            data_venc = parse_date(xml_findtext(prod, 'dVal') or xml_findtext(prod, 'dVenc'))
            quantidade = parse_decimal(xml_findtext(prod, 'qCom') or xml_findtext(prod, 'qTrib'))
            if quantidade <= 0:
                continue

            preco_custo_unitario = parse_decimal(xml_findtext(prod, 'vUnCom'))
            quantidade = parse_decimal(xml_findtext(prod, 'qCom') or xml_findtext(prod, 'qTrib'))
            preco_custo_item = preco_custo_unitario
            if preco_custo_item == 0:
                valor_total = parse_decimal(xml_findtext(prod, 'vProd'))
                if valor_total > 0 and quantidade > 0:
                    preco_custo_item = valor_total / quantidade

            ncm = xml_findtext(prod, 'NCM')

            produto = get_or_create_produto(
                codigo or nome,
                nome,
                codigo,
                current_user.empresa_id,
                preco_custo=preco_custo_item,
                ncm=ncm
            )
            atualizar_grade_estoque(produto, fornecedor, lote, data_venc, int(round(quantidade)))

        conta_existente = ContaPagar.query.filter_by(
            fornecedor_id=fornecedor.id,
            numero_nota_fiscal=numero_nota_fiscal,
            empresa_id=current_user.empresa_id
        ).first()
        
        if conta_existente:
            data_fmt = conta_existente.data_entrada.strftime('%d/%m/%Y')
            flash(f'NFe {numero_nota_fiscal} já foi importada anteriormente em {data_fmt}.', 'warning')
            return redirect(url_for('importar_nfe'))

        conta = ContaPagar(
            fornecedor_id=fornecedor.id,
            numero_nota_fiscal=numero_nota_fiscal,
            data_entrada=data_entrada,
            data_vencimento=data_vencimento,
            valor=total_nota,
            observacoes=f'Importado da NFe {numero_nota_fiscal}',
            usuario_cadastro=current_user.id,
            empresa_id=current_user.empresa_id
        )
        db.session.add(conta)
        db.session.commit()

        flash('NFe importada com sucesso e estoque atualizado.', 'success')
        return redirect(url_for('contas_pagar'))

    return render_template('importar_nfe.html')

# Rotas para Contas a Pagar
@app.route('/contas-pagar')
@login_required
def contas_pagar():
    filtros = {
        'fornecedor_id': request.args.get('fornecedor_id', ''),
        'numero_nota': request.args.get('numero_nota', ''),
        'data_inicio': request.args.get('data_inicio', ''),
        'data_fim': request.args.get('data_fim', '')
    }
    
    query = ContaPagar.query.filter_by(empresa_id=current_user.empresa_id, status='Aberto')
    
    if filtros['fornecedor_id']:
        query = query.filter_by(fornecedor_id=int(filtros['fornecedor_id']))
    if filtros['numero_nota']:
        query = query.filter(ContaPagar.numero_nota_fiscal.ilike(f"%{filtros['numero_nota']}%"))
    if filtros['data_inicio']:
        data_inicio = datetime.strptime(filtros['data_inicio'], '%Y-%m-%d')
        query = query.filter(ContaPagar.data_vencimento >= data_inicio)
    if filtros['data_fim']:
        data_fim = datetime.strptime(filtros['data_fim'], '%Y-%m-%d')
        query = query.filter(ContaPagar.data_vencimento <= data_fim)
    
    contas = query.order_by(ContaPagar.data_vencimento).all()
    total_aberto = sum(float(conta.valor or 0) for conta in contas)
    fornecedores = Fornecedor.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all()
    
    return render_template('contas_pagar.html', contas=contas, total=total_aberto, fornecedores=fornecedores, filtros=filtros, now=datetime.utcnow())

@app.route('/contas-pagar-pagas')
@login_required
def contas_pagar_pagas():
    filtros = {
        'fornecedor_id': request.args.get('fornecedor_id', ''),
        'numero_nota': request.args.get('numero_nota', ''),
        'data_inicio': request.args.get('data_inicio', ''),
        'data_fim': request.args.get('data_fim', '')
    }
    
    query = ContaPagar.query.filter_by(empresa_id=current_user.empresa_id, status='Pago')
    
    if filtros['fornecedor_id']:
        query = query.filter_by(fornecedor_id=int(filtros['fornecedor_id']))
    if filtros['numero_nota']:
        query = query.filter(ContaPagar.numero_nota_fiscal.ilike(f"%{filtros['numero_nota']}%"))
    if filtros['data_inicio']:
        data_inicio = datetime.strptime(filtros['data_inicio'], '%Y-%m-%d')
        query = query.filter(ContaPagar.data_pagamento >= data_inicio)
    if filtros['data_fim']:
        data_fim = datetime.strptime(filtros['data_fim'], '%Y-%m-%d')
        query = query.filter(ContaPagar.data_pagamento <= data_fim)
    
    contas = query.order_by(ContaPagar.data_pagamento.desc()).all()
    total_pagas = sum(float(conta.valor or 0) for conta in contas)
    fornecedores = Fornecedor.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all()
    
    return render_template('contas_pagar_pagas.html', contas=contas, total=total_pagas, fornecedores=fornecedores, filtros=filtros, now=datetime.utcnow())

@app.route('/contas-pagar/novo', methods=['GET', 'POST'])
@login_required
def novo_conta_pagar():
    if request.method == 'POST':
        fornecedor_id = request.form.get('fornecedor_id')
        numero_nota_fiscal = request.form.get('numero_nota_fiscal')
        data_entrada = request.form.get('data_entrada')
        data_vencimento = request.form.get('data_vencimento')
        valor = request.form.get('valor')
        observacoes = request.form.get('observacoes')
        
        if not fornecedor_id:
            flash('Fornecedor é obrigatório.', 'error')
            return render_template('novo_conta_pagar.html', fornecedores=Fornecedor.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all())
        
        if not numero_nota_fiscal:
            flash('Número da nota fiscal é obrigatório.', 'error')
            return render_template('novo_conta_pagar.html', fornecedores=Fornecedor.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all())
        
        if not valor:
            flash('Valor é obrigatório.', 'error')
            return render_template('novo_conta_pagar.html', fornecedores=Fornecedor.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all())
        
        try:
            data_entrada = datetime.strptime(data_entrada, '%Y-%m-%d')
            data_vencimento = datetime.strptime(data_vencimento, '%Y-%m-%d')
            # Aceitar tanto vírgula quanto ponto como separador decimal
            valor = float(valor.replace(',', '.'))
        except ValueError:
            flash('Formato de data ou valor inválido.', 'error')
            return render_template('novo_conta_pagar.html', fornecedores=Fornecedor.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all())
        
        conta = ContaPagar(
            fornecedor_id=int(fornecedor_id),
            numero_nota_fiscal=numero_nota_fiscal,
            data_entrada=data_entrada,
            data_vencimento=data_vencimento,
            valor=valor,
            observacoes=observacoes,
            usuario_cadastro=current_user.id,
            empresa_id=current_user.empresa_id
        )
        
        db.session.add(conta)
        db.session.commit()
        
        flash('Conta a pagar cadastrada com sucesso!', 'success')
        return redirect(url_for('contas_pagar'))
    
    fornecedores = Fornecedor.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all()
    return render_template('novo_conta_pagar.html', fornecedores=fornecedores)

# Rotas para Bancos
@app.route('/bancos')
@login_required
def bancos():
    bancos_list = Banco.query.filter_by(empresa_id=current_user.empresa_id).order_by(Banco.nome).all()
    return render_template('bancos.html', bancos=bancos_list)

@app.route('/bancos/novo', methods=['GET', 'POST'])
@login_required
def novo_banco():
    if request.method == 'POST':
        nome = request.form.get('nome')
        numero_banco = request.form.get('numero_banco')
        agencia = request.form.get('agencia')
        conta = request.form.get('conta')
        tipo_conta = request.form.get('tipo_conta', 'Corrente')
        saldo = request.form.get('saldo', '0')
        
        if not nome:
            flash('Nome é obrigatório.', 'error')
            return render_template('novo_banco.html')
        
        if not numero_banco or not agencia or not conta:
            flash('Número do banco, agência e conta são obrigatórios.', 'error')
            return render_template('novo_banco.html')
        
        try:
            saldo = parse_decimal(saldo)
        except:
            flash('Saldo inválido.', 'error')
            return render_template('novo_banco.html')
        
        # Verificar se já existe
        existe = Banco.query.filter_by(numero_banco=numero_banco, agencia=agencia, conta=conta, empresa_id=current_user.empresa_id).first()
        if existe:
            flash('Já existe uma conta bancária com esses dados.', 'error')
            return render_template('novo_banco.html')
        
        banco = Banco(
            nome=nome,
            numero_banco=numero_banco,
            agencia=agencia,
            conta=conta,
            tipo_conta=tipo_conta,
            saldo=saldo,
            usuario_cadastro=current_user.id,
            empresa_id=current_user.empresa_id
        )
        
        db.session.add(banco)
        db.session.commit()
        
        flash('Banco cadastrado com sucesso!', 'success')
        return redirect(url_for('bancos'))
    
    return render_template('novo_banco.html')

@app.route('/bancos/<int:banco_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_banco(banco_id):
    banco = Banco.query.get_or_404(banco_id)
    
    if banco.empresa_id != current_user.empresa_id:
        abort(403)
    
    if request.method == 'POST':
        banco.nome = request.form.get('nome', banco.nome)
        banco.numero_banco = request.form.get('numero_banco', banco.numero_banco)
        banco.agencia = request.form.get('agencia', banco.agencia)
        banco.conta = request.form.get('conta', banco.conta)
        banco.tipo_conta = request.form.get('tipo_conta', banco.tipo_conta)
        banco.ativo = request.form.get('ativo') == 'on'
        
        try:
            saldo = request.form.get('saldo', str(banco.saldo))
            banco.saldo = parse_decimal(saldo)
        except:
            flash('Saldo inválido.', 'error')
            return render_template('editar_banco.html', banco=banco)
        
        db.session.commit()
        flash('Banco atualizado com sucesso!', 'success')
        return redirect(url_for('bancos'))
    
    return render_template('editar_banco.html', banco=banco)

@app.route('/bancos/<int:banco_id>/deletar')
@login_required
def deletar_banco(banco_id):
    banco = Banco.query.get_or_404(banco_id)
    
    if banco.empresa_id != current_user.empresa_id:
        abort(403)
    
    # Verificar se tem movimentações
    movimentacoes = MovimentacaoBancaria.query.filter_by(banco_id=banco_id).count()
    if movimentacoes > 0:
        flash('Não é possível deletar um banco com movimentações.', 'error')
        return redirect(url_for('bancos'))
    
    db.session.delete(banco)
    db.session.commit()
    
    flash('Banco deletado com sucesso!', 'success')
    return redirect(url_for('bancos'))

# Rotas para baixar contas
@app.route('/contas-pagar/<int:conta_id>/baixar', methods=['GET', 'POST'])
@login_required
def baixar_conta_pagar(conta_id):
    conta = ContaPagar.query.get_or_404(conta_id)
    
    if conta.empresa_id != current_user.empresa_id:
        abort(403)
    
    if request.method == 'POST':
        banco_id = request.form.get('banco_id')
        valor_pago_str = request.form.get('valor_pago', str(conta.valor))
        
        if not banco_id:
            flash('Selecione um banco.', 'error')
            bancos_list = Banco.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all()
            return render_template('baixar_conta_pagar.html', conta=conta, bancos=bancos_list)
        
        try:
            valor_pago = parse_decimal(valor_pago_str)
            banco_id = int(banco_id)
        except:
            flash('Valor ou banco inválido.', 'error')
            bancos_list = Banco.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all()
            return render_template('baixar_conta_pagar.html', conta=conta, bancos=bancos_list)
        
        banco = Banco.query.get_or_404(banco_id)
        
        if banco.empresa_id != current_user.empresa_id:
            abort(403)
        
        # Atualizar conta
        conta.valor_pago = valor_pago
        conta.data_pagamento = datetime.now()
        conta.status = 'Pago'
        conta.banco_id = banco_id
        
        # Atualizar saldo do banco
        banco.saldo = float(banco.saldo) - valor_pago
        
        # Registrar movimentação
        movimentacao = MovimentacaoBancaria(
            banco_id=banco_id,
            tipo='Saída',
            descricao=f'Pagamento NFe {conta.numero_nota_fiscal} - {conta.fornecedor.razao_social}',
            valor=valor_pago,
            saldo_anterior=float(banco.saldo) + valor_pago,
            saldo_novo=float(banco.saldo),
            conta_pagar_id=conta_id,
            usuario_id=current_user.id,
            empresa_id=current_user.empresa_id
        )
        
        db.session.add(movimentacao)
        db.session.commit()
        
        flash(f'Conta paga com sucesso! Saldo do banco: R$ {banco.saldo:.2f}', 'success')
        return redirect(url_for('contas_pagar'))
    
    bancos_list = Banco.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all()
    return render_template('baixar_conta_pagar.html', conta=conta, bancos=bancos_list)

@app.route('/contas-receber/<int:conta_id>/baixar', methods=['GET', 'POST'])
@login_required
def baixar_conta_receber(conta_id):
    conta = ContaReceber.query.get_or_404(conta_id)
    
    if conta.empresa_id != current_user.empresa_id:
        abort(403)
    
    if request.method == 'POST':
        banco_id = request.form.get('banco_id')
        valor_pago_str = request.form.get('valor_pago', str(conta.valor_parcela))
        
        if not banco_id:
            flash('Selecione um banco.', 'error')
            bancos_list = Banco.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all()
            return render_template('baixar_conta_receber.html', conta=conta, bancos=bancos_list)
        
        try:
            valor_pago = parse_decimal(valor_pago_str)
            banco_id = int(banco_id)
        except:
            flash('Valor ou banco inválido.', 'error')
            bancos_list = Banco.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all()
            return render_template('baixar_conta_receber.html', conta=conta, bancos=bancos_list)
        
        banco = Banco.query.get_or_404(banco_id)
        
        if banco.empresa_id != current_user.empresa_id:
            abort(403)
        
        # Atualizar conta
        conta.valor_pago = valor_pago
        conta.data_pagamento = datetime.now()
        conta.status = 'Pago'
        conta.banco_id = banco_id
        
        # Atualizar saldo do banco
        banco.saldo = float(banco.saldo) + valor_pago
        
        # Registrar movimentação
        if conta.venda:
            descricao = f'Recebimento - Cliente: {conta.cliente.nome} - Parcela {conta.numero_parcela}/{conta.venda.numero_parcelas}'
        else:
            descricao = f'Recebimento - Cliente: {conta.cliente.nome} - Conta Avulsa'
        
        movimentacao = MovimentacaoBancaria(
            banco_id=banco_id,
            tipo='Entrada',
            descricao=descricao,
            valor=valor_pago,
            saldo_anterior=float(banco.saldo) - valor_pago,
            saldo_novo=float(banco.saldo),
            conta_receber_id=conta_id,
            usuario_id=current_user.id,
            empresa_id=current_user.empresa_id
        )
        
        db.session.add(movimentacao)
        db.session.commit()
        
        flash(f'Parcela recebida com sucesso! Saldo do banco: R$ {banco.saldo:.2f}', 'success')
        return redirect(url_for('contas_receber'))
    
    bancos_list = Banco.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all()
    return render_template('baixar_conta_receber.html', conta=conta, bancos=bancos_list)

# Rotas para Vendedores
@app.route('/vendedores')
@login_required
def vendedores():
    vendedores = Vendedor.query.filter_by(empresa_id=current_user.empresa_id).order_by(Vendedor.nome).all()
    return render_template('vendedores.html', vendedores=vendedores)

@app.route('/vendedores/novo', methods=['GET', 'POST'])
@login_required
def novo_vendedor():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        comissao = request.form.get('comissao')
        ativo = request.form.get('ativo') == 'on'
        
        # Validações
        if not nome:
            flash('Nome do vendedor é obrigatório.', 'error')
            return render_template('novo_vendedor.html')
        
        if not validar_cpf(cpf):
            flash('CPF inválido.', 'error')
            return render_template('novo_vendedor.html')
        
        if Vendedor.query.filter_by(cpf=cpf, empresa_id=current_user.empresa_id).first():
            flash('CPF já cadastrado nesta empresa.', 'error')
            return render_template('novo_vendedor.html')
        
        # Converter comissão
        try:
            comissao = float(comissao) if comissao else 0
        except ValueError:
            flash('Comissão deve ser um número válido.', 'error')
            return render_template('novo_vendedor.html')
        
        # Criar novo vendedor
        vendedor = Vendedor(
            nome=nome,
            cpf=formatar_cpf(cpf),
            email=email,
            telefone=formatar_telefone(telefone) if telefone else None,
            comissao=comissao,
            ativo=ativo,
            usuario_cadastro=current_user.id,
            empresa_id=current_user.empresa_id
        )
        
        db.session.add(vendedor)
        db.session.commit()
        
        flash('Vendedor cadastrado com sucesso!', 'success')
        return redirect(url_for('vendedores'))
    
    return render_template('novo_vendedor.html')

# Rotas para Grupos de Produtos
@app.route('/grupos')
@login_required
def grupos():
    grupos = GrupoProduto.query.filter_by(empresa_id=current_user.empresa_id).order_by(GrupoProduto.nome).all()
    return render_template('grupos.html', grupos=grupos)

@app.route('/grupos/novo', methods=['GET', 'POST'])
@login_required
def novo_grupo():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        ativo = request.form.get('ativo') == 'on'
        
        # Validações
        if not nome:
            flash('Nome do grupo é obrigatório.', 'error')
            return render_template('novo_grupo.html')
        
        if GrupoProduto.query.filter_by(nome=nome, empresa_id=current_user.empresa_id).first():
            flash('Já existe um grupo com este nome.', 'error')
            return render_template('novo_grupo.html')
        
        # Criar novo grupo
        grupo = GrupoProduto(
            nome=nome,
            descricao=descricao,
            ativo=ativo,
            usuario_cadastro=current_user.id,
            empresa_id=current_user.empresa_id
        )
        
        db.session.add(grupo)
        db.session.commit()
        
        flash('Grupo de produtos criado com sucesso!', 'success')
        return redirect(url_for('grupos'))
    
    return render_template('novo_grupo.html')

# Rotas para Produtos
@app.route('/produtos')
@login_required
def produtos():
    produtos = Produto.query.filter_by(empresa_id=current_user.empresa_id).join(GrupoProduto).order_by(GrupoProduto.nome, Produto.nome).all()
    return render_template('produtos.html', produtos=produtos)

@app.route('/produtos/novo', methods=['GET', 'POST'])
@login_required
def novo_produto():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        marca = request.form.get('marca')
        ncm = request.form.get('ncm')
        preco_custo = request.form.get('preco_custo')
        preco_venda = request.form.get('preco_venda')
        estoque = request.form.get('estoque')
        estoque_minimo = request.form.get('estoque_minimo')
        grupo_id = request.form.get('grupo_id')
        ativo = request.form.get('ativo') == 'on'
        
        # Validações
        if not codigo:
            flash('Código do produto é obrigatório.', 'error')
            return render_template('novo_produto.html', grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all())
        
        if not nome:
            flash('Nome do produto é obrigatório.', 'error')
            return render_template('novo_produto.html', grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all())
        
        if not preco_venda:
            flash('Preço de venda é obrigatório.', 'error')
            return render_template('novo_produto.html', grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all())
        
        if not grupo_id:
            flash('Grupo do produto é obrigatório.', 'error')
            return render_template('novo_produto.html', grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all())
        
        if Produto.query.filter_by(codigo=codigo, empresa_id=current_user.empresa_id).first():
            flash('Já existe um produto com este código.', 'error')
            return render_template('novo_produto.html', grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all())
        
        # Converter valores
        try:
            preco_custo = parse_decimal(preco_custo) if preco_custo else None
            preco_venda = parse_decimal(preco_venda)
            estoque = int(estoque) if estoque else 0
            estoque_minimo = int(estoque_minimo) if estoque_minimo else 0
            grupo_id = int(grupo_id)
        except ValueError:
            flash('Valores numéricos inválidos.', 'error')
            return render_template('novo_produto.html', grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all())
        
        # Criar novo produto
        produto = Produto(
            codigo=codigo,
            nome=nome,
            descricao=descricao,
            marca=marca,
            ncm=ncm,
            preco_custo=preco_custo,
            preco_venda=preco_venda,
            estoque=estoque,
            estoque_minimo=estoque_minimo,
            grupo_id=grupo_id,
            ativo=ativo,
            usuario_cadastro=current_user.id,
            empresa_id=current_user.empresa_id
        )
        
        db.session.add(produto)
        db.session.commit()
        
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('produtos'))
    
    return render_template('novo_produto.html', grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all())

@app.route('/produtos/<int:produto_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_produto(produto_id):
    produto = Produto.query.filter_by(id=produto_id, empresa_id=current_user.empresa_id).first()
    if produto is None:
        abort(404)

    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        marca = request.form.get('marca')
        ncm = request.form.get('ncm')
        preco_custo = request.form.get('preco_custo')
        preco_venda = request.form.get('preco_venda')
        estoque = request.form.get('estoque')
        estoque_minimo = request.form.get('estoque_minimo')
        grupo_id = request.form.get('grupo_id')
        ativo = request.form.get('ativo') == 'on'

        if not codigo:
            flash('Código do produto é obrigatório.', 'error')
            return render_template('editar_produto.html', produto=produto, grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all())

        if not nome:
            flash('Nome do produto é obrigatório.', 'error')
            return render_template('editar_produto.html', produto=produto, grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all())

        if not preco_venda:
            flash('Preço de venda é obrigatório.', 'error')
            return render_template('editar_produto.html', produto=produto, grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all())

        if not grupo_id:
            flash('Grupo do produto é obrigatório.', 'error')
            return render_template('editar_produto.html', produto=produto, grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all())

        produto_existente = Produto.query.filter_by(codigo=codigo, empresa_id=current_user.empresa_id).first()
        if produto_existente and produto_existente.id != produto.id:
            flash('Já existe um produto com este código.', 'error')
            return render_template('editar_produto.html', produto=produto, grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all())

        try:
            preco_custo = parse_decimal(preco_custo) if preco_custo else None
            preco_venda = parse_decimal(preco_venda)
            estoque = int(estoque) if estoque else 0
            estoque_minimo = int(estoque_minimo) if estoque_minimo else 0
            grupo_id = int(grupo_id)
        except ValueError:
            flash('Valores numéricos inválidos.', 'error')
            return render_template('editar_produto.html', produto=produto, grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all())

        produto.codigo = codigo
        produto.nome = nome
        produto.descricao = descricao
        produto.marca = marca
        produto.ncm = ncm
        produto.preco_custo = preco_custo
        produto.preco_venda = preco_venda
        produto.estoque = estoque
        produto.estoque_minimo = estoque_minimo
        produto.grupo_id = grupo_id
        produto.ativo = ativo

        db.session.commit()

        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('produtos'))

    return render_template('editar_produto.html', produto=produto, grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all())

# Rotas para Vendas
@app.route('/vendas')
@login_required
def vendas():
    # Parâmetros de filtro
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    cliente_id = request.args.get('cliente_id')
    vendedor_id = request.args.get('vendedor_id')
    
    # Query base
    if current_user.admin:
        query = Venda.query.filter_by(excluido=False, empresa_id=current_user.empresa_id)
    else:
        query = Venda.query.filter_by(excluido=False, usuario_cadastro=current_user.id, empresa_id=current_user.empresa_id)
    
    # Aplicar filtros
    if data_inicio:
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Venda.data_venda >= data_inicio)
        except ValueError:
            pass
    
    if data_fim:
        try:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
            # Adicionar 23:59:59 para incluir todo o dia
            data_fim = data_fim.replace(hour=23, minute=59, second=59)
            query = query.filter(Venda.data_venda <= data_fim)
        except ValueError:
            pass
    
    if cliente_id:
        query = query.filter(Venda.cliente_id == cliente_id)
    
    if vendedor_id:
        query = query.filter(Venda.vendedor_id == vendedor_id)
    
    # Ordenar por data mais recente
    vendas = query.order_by(Venda.data_venda.desc()).all()
    
    # Buscar clientes e vendedores para os filtros
    clientes = Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Cliente.nome).all()
    vendedores = Vendedor.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Vendedor.nome).all()
    
    return render_template('vendas.html', 
                         vendas=vendas, 
                         clientes=clientes, 
                         vendedores=vendedores,
                         filtros={
                             'data_inicio': data_inicio,
                             'data_fim': data_fim,
                             'cliente_id': cliente_id,
                             'vendedor_id': vendedor_id
                         })

@app.route('/vendas/nova', methods=['GET', 'POST'])
@login_required
def nova_venda():
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        vendedor_id = request.form.get('vendedor_id')
        forma_pagamento = request.form.get('forma_pagamento')
        desconto = request.form.get('desconto')
        observacoes = request.form.get('observacoes')
        
        # Validações
        if not cliente_id:
            flash('Cliente é obrigatório.', 'error')
            return render_template('venda_grade.html', 
                                clientes=Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all(),
                                vendedores=Vendedor.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all(),
                                grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all(),
                                data_hoje=datetime.now().date().isoformat())
        
        if not vendedor_id:
            flash('Vendedor é obrigatório.', 'error')
            return render_template('venda_grade.html', 
                                clientes=Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all(),
                                vendedores=Vendedor.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all(),
                                grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all(),
                                data_hoje=datetime.now().date().isoformat())
        
        # Converter desconto
        try:
            desconto = float(desconto) if desconto else 0
        except ValueError:
            flash('Desconto deve ser um número válido.', 'error')
            return render_template('venda_grade.html', 
                                clientes=Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all(),
                                vendedores=Vendedor.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all(),
                                grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all(),
                                data_hoje=datetime.now().date().isoformat())
        
        # Criar venda
        venda = Venda(
            numero_venda=gerar_numero_venda(),
            cliente_id=int(cliente_id),
            vendedor_id=int(vendedor_id),
            forma_pagamento=forma_pagamento,
            desconto=desconto,
            subtotal=0,
            total=0,
            status='Pendente',
            observacoes=observacoes,
            usuario_cadastro=current_user.id,
            empresa_id=current_user.empresa_id
        )
        
        db.session.add(venda)
        db.session.commit()
        
        flash('Venda iniciada com sucesso!', 'success')
        return redirect(url_for('vendas'))
    
    from datetime import date
    data_hoje = date.today().isoformat()
    return render_template('venda_grade.html', 
                         clientes=Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all(),
                         vendedores=Vendedor.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all(),
                         grupos=GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all(),
                         data_hoje=data_hoje)

@app.route('/vendas/gravar', methods=['POST'])
@login_required
def gravar_venda():
    data = request.get_json()
    cliente_id = data.get('cliente_id')
    vendedor_id = data.get('vendedor_id')
    data_emissao = data.get('data_emissao')
    itens = data.get('itens', [])
    observacoes = data.get('observacoes', '')
    forma_pagamento = data.get('forma_pagamento', 'Dinheiro')
    tipo_pagamento = data.get('tipo_pagamento', 'A Vista')
    tipo_parcelamento = data.get('tipo_parcelamento', 'A Vista')
    numero_parcelas = int(data.get('numero_parcelas', 1))  # Converter para int
    dias_parcelas = data.get('dias_parcelas', [])  # Array de dias para cada parcela

    if not cliente_id or not vendedor_id or not itens:
        return jsonify({'success': False, 'message': 'Cliente, vendedor e itens são obrigatórios.'}), 400

    try:
        desconto_geral = float(data.get('desconto_geral', 0))
        subtotal = 0
        itens_para_gravar = []
        for item in itens:
            if int(item['quantidade']) > 0:
                preco = float(item['preco'])
                quantidade = int(item['quantidade'])
                desconto = float(item.get('desconto', 0))
                subtotal_item = (preco * quantidade) - desconto
                subtotal += subtotal_item
                itens_para_gravar.append({
                    'produto_id': int(item['produto_id']),
                    'quantidade': quantidade,
                    'preco_unitario': preco,
                    'desconto': desconto,
                    'subtotal': subtotal_item,
                    'brinde': item.get('brinde', ''),
                    'troca': item.get('troca', '')
                })
        total = subtotal - desconto_geral
        
        # Calcular valor da parcela
        valor_parcela = None
        if tipo_pagamento == 'A Prazo' and numero_parcelas > 1:
            valor_parcela = total / numero_parcelas
        
        from datetime import datetime, timedelta
        venda = Venda(
            numero_venda=gerar_numero_venda(),
            cliente_id=int(cliente_id),
            vendedor_id=int(vendedor_id),
            data_venda=datetime.strptime(data_emissao, '%Y-%m-%d'),
            subtotal=subtotal,
            desconto=desconto_geral,
            total=total,
            forma_pagamento=forma_pagamento,
            tipo_pagamento=tipo_pagamento,
            tipo_parcelamento=tipo_parcelamento,
            numero_parcelas=numero_parcelas,
            dias_entre_parcelas=30,  # Valor padrão, não usado mais
            valor_parcela=valor_parcela,
            status='Pendente',
            observacoes=observacoes,
            usuario_cadastro=current_user.id,
            empresa_id=current_user.empresa_id
        )
        db.session.add(venda)
        db.session.flush()  # Para pegar o id da venda
        
        # Adicionar itens da venda
        def add_item_venda(item):
            db.session.add(ItemVenda(
                venda_id=venda.id,
                produto_id=item['produto_id'],
                quantidade=item['quantidade'],
                preco_unitario=item['preco_unitario'],
                desconto=item['desconto'],
                subtotal=item['subtotal'],
                brinde=item['brinde'],
                troca=item['troca']
            ))
        
        for item in itens_para_gravar:
            add_item_venda(item)
        
        # Criar contas a receber se for a prazo
        if tipo_pagamento == 'A Prazo' and numero_parcelas > 1 and valor_parcela:
            data_base = datetime.strptime(data_emissao, '%Y-%m-%d')
            
            for i in range(1, numero_parcelas + 1):
                # Calcular data de vencimento usando os dias específicos de cada parcela
                dias = dias_parcelas[i - 1] if i - 1 < len(dias_parcelas) else 30
                data_vencimento = data_base + timedelta(days=dias)
                
                conta = ContaReceber(
                    venda_id=venda.id,
                    cliente_id=int(cliente_id),
                    vendedor_id=int(vendedor_id),
                    numero_parcela=i,
                    data_vencimento=data_vencimento,
                    valor_parcela=valor_parcela,
                    status='Pendente',
                    observacoes='',
                    usuario_cadastro=current_user.id,
                    empresa_id=current_user.empresa_id
                )
                db.session.add(conta)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Venda gravada com sucesso!', 'redirect': '/vendas'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao gravar venda: {str(e)}'}), 500

@app.route('/vendas/<int:venda_id>/pdf')
@login_required
def venda_pdf(venda_id):
    if HTML is None:
        return 'WeasyPrint não instalado. Instale com: pip install weasyprint', 500
    venda = Venda.query.get_or_404(venda_id)
    
    # Marcar como impressa
    venda.impresso = True
    db.session.commit()
    
    itens = venda.itens
    cliente = venda.cliente
    vendedor = venda.vendedor
    rendered = render_template('pdf_venda.html', venda=venda, itens=itens, cliente=cliente, vendedor=vendedor)
    pdf_io = io.BytesIO()
    HTML(string=rendered).write_pdf(pdf_io)
    pdf_io.seek(0)
    return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name=f'venda_{venda.numero_venda}.pdf')

# API para buscar produtos por grupo
@app.route('/api/produtos/grupo/<int:grupo_id>')
@login_required
def produtos_por_grupo(grupo_id):
    produtos = Produto.query.filter_by(grupo_id=grupo_id, ativo=True).all()
    return jsonify([{
        'id': p.id,
        'codigo': p.codigo,
        'nome': p.nome,
        'marca': p.marca,
        'preco_venda': float(p.preco_venda),
        'estoque': p.estoque
    } for p in produtos])

@app.route('/vendas/<int:venda_id>/excluir', methods=['POST'])
@login_required
def excluir_venda(venda_id):
    venda = Venda.query.get_or_404(venda_id)
    venda.excluido = True
    db.session.commit()
    flash('Venda excluída com sucesso!', 'success')
    return redirect(url_for('vendas'))

@app.route('/pedido/<int:pedido_id>/visualizar')
@login_required
def visualizar_pedido(pedido_id):
    venda = Venda.query.get_or_404(pedido_id)
    itens = venda.itens
    cliente = venda.cliente
    vendedor = venda.vendedor
    return render_template('visualizar_pedido.html', venda=venda, itens=itens, cliente=cliente, vendedor=vendedor)

@app.route('/contas-receber')
@login_required
def contas_receber():
    # Parâmetros de filtro
    cliente_id = request.args.get('cliente_id')
    vendedor_id = request.args.get('vendedor_id')
    status = request.args.get('status')
    
    # Query base
    query = ContaReceber.query.filter_by(empresa_id=current_user.empresa_id)
    
    # Aplicar filtros
    if cliente_id:
        query = query.filter(ContaReceber.cliente_id == cliente_id)
    
    if vendedor_id:
        query = query.filter(ContaReceber.vendedor_id == vendedor_id)
    
    if status:
        query = query.filter(ContaReceber.status == status)
    
    # Ordenar por data de vencimento
    contas = query.order_by(ContaReceber.data_vencimento).all()
    
    # Buscar clientes e vendedores para os filtros
    clientes = Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Cliente.nome).all()
    vendedores = Vendedor.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Vendedor.nome).all()
    
    # Data atual para comparação de vencimento
    hoje = datetime.now().date()
    
    return render_template('contas_receber.html', 
                         contas=contas, 
                         clientes=clientes, 
                         vendedores=vendedores,
                         hoje=hoje,
                         filtros={
                             'cliente_id': cliente_id,
                             'vendedor_id': vendedor_id,
                             'status': status
                         })

@app.route('/contas-receber/<int:conta_id>/pagar', methods=['POST'])
@login_required
def pagar_conta(conta_id):
    try:
        conta = ContaReceber.query.get_or_404(conta_id)
        valor_pago_str = request.form.get('valor_pago')
        valor_pago = float(valor_pago_str) if valor_pago_str else float(conta.valor_parcela)
        
        # Atualizar dados da conta
        conta.valor_pago = valor_pago
        conta.data_pagamento = datetime.now()
        conta.status = 'Pago'
        
        db.session.commit()
        
        # Gerar recibo
        recibo_texto = gerar_recibo(conta)
        
        # Redirecionar automaticamente para a página do recibo
        return redirect(url_for('imprimir_recibo', conta_id=conta.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao pagar parcela: {str(e)}', 'error')
        return redirect(url_for('contas_receber'))

@app.route('/contas-receber/nova-avulsa', methods=['GET', 'POST'])
@login_required
def nova_conta_receber_avulsa():
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        data_vencimento = request.form.get('data_vencimento')
        valor = request.form.get('valor')
        observacoes = request.form.get('observacoes')
        
        if not cliente_id:
            flash('Cliente é obrigatório.', 'error')
            clientes = Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Cliente.nome).all()
            return render_template('nova_conta_receber_avulsa.html', clientes=clientes)
        
        if not data_vencimento:
            flash('Data de vencimento é obrigatória.', 'error')
            clientes = Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Cliente.nome).all()
            return render_template('nova_conta_receber_avulsa.html', clientes=clientes)
        
        if not valor:
            flash('Valor é obrigatório.', 'error')
            clientes = Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Cliente.nome).all()
            return render_template('nova_conta_receber_avulsa.html', clientes=clientes)
        
        try:
            data_vencimento = datetime.strptime(data_vencimento, '%Y-%m-%d')
            valor = float(valor.replace(',', '.'))
        except ValueError:
            flash('Formato de data ou valor inválido.', 'error')
            clientes = Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Cliente.nome).all()
            return render_template('nova_conta_receber_avulsa.html', clientes=clientes)
        
        conta = ContaReceber(
            cliente_id=int(cliente_id),
            data_vencimento=data_vencimento,
            valor_parcela=valor,
            numero_parcela=1,
            tipo_conta='Avulsa',
            status='Pendente',
            observacoes=observacoes,
            usuario_cadastro=current_user.id,
            empresa_id=current_user.empresa_id
        )
        
        db.session.add(conta)
        db.session.commit()
        
        flash('Conta a receber avulsa cadastrada com sucesso!', 'success')
        return redirect(url_for('contas_receber'))
    
    clientes = Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Cliente.nome).all()
    return render_template('nova_conta_receber_avulsa.html', clientes=clientes)

def gerar_recibo(conta):
    """Gera recibo de pagamento"""
    from datetime import datetime
    
    # Construir informações sobre a venda/conta
    info_venda = ""
    if conta.venda:
        info_venda = f"""
    VENDA:
    Número: {conta.venda.numero_venda}
    Parcela: {conta.numero_parcela}/{conta.venda.numero_parcelas}"""
    else:
        info_venda = f"""
    CONTA:
    Tipo: Avulsa
    Descrição: {conta.observacoes if conta.observacoes else 'Sem descrição'}"""
    
    # Informações do vendedor
    info_vendedor = ""
    if conta.vendedor:
        info_vendedor = f"""
    Vendedor: {conta.vendedor.nome}"""
    
    recibo_texto = f"""
    ========================================
              RECIBO DE PAGAMENTO
    ========================================
    
    Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    Recibo Nº: {conta.id:06d}
    
    ========================================
    CLIENTE:
    Nome: {conta.cliente.nome}
    CPF: {conta.cliente.cpf}{info_venda}
    
    ========================================
    VALOR PAGO: R$ {conta.valor_pago:.2f}
    ========================================{info_vendedor}
    
    ========================================
    Assinatura: _________________
    ========================================
    
    """
    
    # Salvar recibo no banco (opcional)
    # Aqui você pode salvar o recibo em uma tabela se necessário
    
    return recibo_texto

@app.route('/contas-receber/<int:conta_id>/recibo')
@login_required
def imprimir_recibo(conta_id):
    conta = ContaReceber.query.get_or_404(conta_id)
    
    if conta.status != 'Pago':
        flash('Apenas parcelas pagas podem gerar recibo!', 'error')
        return redirect(url_for('contas_receber'))
    
    recibo_texto = gerar_recibo(conta)
    
    # Retornar como texto simples para impressão
    return recibo_texto, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/contas-receber/<int:conta_id>/imprimir-bluetooth')
@login_required
def imprimir_bluetooth(conta_id):
    conta = ContaReceber.query.get_or_404(conta_id)
    
    if conta.status != 'Pago':
        return jsonify({'success': False, 'message': 'Apenas parcelas pagas podem gerar recibo!'})
    
    try:
        from config_impressora import ImpressoraCoojprt
        
        impressora = ImpressoraCoojprt(porta_serial="COM10")
        
        # Preparar dados do recibo
        dados_recibo = {
            'data': conta.data_pagamento.strftime('%d/%m/%Y %H:%M'),
            'numero': conta.id,
            'cliente_nome': conta.cliente.nome,
            'cliente_cpf': conta.cliente.cpf,
            'valor': float(conta.valor_pago),
        }
        
        # Adicionar informações sobre venda se existir
        if conta.venda:
            dados_recibo['venda_numero'] = conta.venda.numero_venda
            dados_recibo['parcela'] = conta.numero_parcela
            dados_recibo['total_parcelas'] = conta.venda.numero_parcelas
        else:
            dados_recibo['venda_numero'] = 'Avulsa'
            dados_recibo['parcela'] = 'N/A'
            dados_recibo['total_parcelas'] = 'N/A'
        
        # Adicionar vendedor se existir
        if conta.vendedor:
            dados_recibo['vendedor'] = conta.vendedor.nome
        else:
            dados_recibo['vendedor'] = 'Sem vendedor'
        
        if impressora.imprimir_recibo_serial(dados_recibo):
            return jsonify({'success': True, 'message': 'Recibo enviado para impressora via serial (COM10)!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao imprimir via serial (COM10)!'})
        
    except ImportError:
        return jsonify({'success': False, 'message': 'Biblioteca pyserial não instalada. Execute: pip install pyserial'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao imprimir: {str(e)}'})

@app.route('/api/cep/<cep>')
def consultar_cep(cep):
    """Consulta CEP via API externa"""
    import requests
    
    cep_limpo = re.sub(r'[^0-9]', '', cep)
    
    if len(cep_limpo) != 8:
        return jsonify({'erro': 'CEP inválido'})
    
    try:
        response = requests.get(f'https://viacep.com.br/ws/{cep_limpo}/json/')
        data = response.json()
        
        if 'erro' in data:
            return jsonify({'erro': 'CEP não encontrado'})
        
        return jsonify({
            'endereco': data.get('logradouro', ''),
            'bairro': data.get('bairro', ''),
            'cidade': data.get('localidade', ''),
            'estado': data.get('uf', '')
        })
    except:
        return jsonify({'erro': 'Erro ao consultar CEP'})

@app.route('/api/cnpj/<cnpj>')
def consultar_cnpj(cnpj):
    """Consulta CNPJ via API da Receita Federal"""
    import requests
    import urllib3
    
    # Desabilitar aviso de SSL (apenas para desenvolvimento)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
    
    if len(cnpj_limpo) != 14:
        return jsonify({'erro': 'CNPJ inválido'})
    
    try:
        # Tentar usar a API CNPJ.ws primeiro
        try:
            response = requests.get(f'https://www.cnpj.ws/cnpj/{cnpj_limpo}', verify=False)
            data = response.json()
            
            if 'erro' not in data and 'status' not in data:
                return jsonify({
                    'razao_social': data.get('razao_social', ''),
                    'nome_fantasia': data.get('nome_fantasia', ''),
                    'email': data.get('email', ''),
                    'telefone': data.get('telefone', ''),
                    'cep': data.get('cep', ''),
                    'endereco': data.get('logradouro', ''),
                    'numero': data.get('numero', ''),
                    'complemento': data.get('complemento', ''),
                    'bairro': data.get('bairro', ''),
                    'cidade': data.get('municipio', ''),
                    'estado': data.get('uf', ''),
                    'inscricao_estadual': data.get('inscricao_estadual', '')
                })
        except:
            pass
        
        # Tentar usar a API BrasilAPI
        try:
            response = requests.get(f'https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}', verify=False)
            data = response.json()
            
            if 'erro' not in data:
                return jsonify({
                    'razao_social': data.get('razao_social', ''),
                    'nome_fantasia': data.get('nome_fantasia', ''),
                    'email': data.get('email', ''),
                    'telefone': data.get('ddd_telefone_1', ''),
                    'cep': data.get('cep', ''),
                    'endereco': data.get('logradouro', ''),
                    'numero': data.get('numero', ''),
                    'complemento': data.get('complemento', ''),
                    'bairro': data.get('bairro', ''),
                    'cidade': data.get('municipio', ''),
                    'estado': data.get('uf', ''),
                    'inscricao_estadual': data.get('inscricoes_estaduais', [{}])[0].get('inscricao_estadual', '') if data.get('inscricoes_estaduais') else ''
                })
        except:
            pass
        
        # Fallback para API receitaws
        response = requests.get(f'https://receitaws.com.br/v1/cnpj/{cnpj_limpo}', verify=False)
        data = response.json()
        
        if 'status' in data and data['status'] == 'ERROR':
            return jsonify({'erro': data.get('message', 'CNPJ não encontrado')})
        
        return jsonify({
            'razao_social': data.get('nome', ''),
            'nome_fantasia': data.get('fantasia', ''),
            'email': data.get('email', ''),
            'telefone': data.get('telefone', ''),
            'cep': data.get('cep', ''),
            'endereco': data.get('logradouro', ''),
            'numero': data.get('numero', ''),
            'complemento': data.get('complemento', ''),
            'bairro': data.get('bairro', ''),
            'cidade': data.get('municipio', ''),
            'estado': data.get('uf', ''),
            'inscricao_estadual': data.get('ie', '')
        })
    except Exception as e:
        return jsonify({'erro': f'Erro ao consultar CNPJ: {str(e)}'})

@app.route('/api/recibo/ultimo', methods=['GET'])
def api_recibo_ultimo():
    # Busca a última parcela paga e não excluída
    conta = ContaReceber.query.filter_by(status='Pago').order_by(ContaReceber.data_pagamento.desc()).first()
    if not conta:
        return jsonify({'success': False, 'message': 'Nenhum recibo disponível.'}), 404
    recibo_texto = gerar_recibo(conta)
    return jsonify({
        'success': True,
        'conta_id': conta.id,
        'recibo': recibo_texto
    })

@app.route('/api/recibo/<int:conta_id>/excluir', methods=['POST'])
def api_recibo_excluir(conta_id):
    conta = ContaReceber.query.get_or_404(conta_id)
    try:
        # Marca como excluído (ou pode remover do banco, se preferir)
        conta.status = 'Excluido'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Recibo excluído com sucesso.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao excluir recibo: {str(e)}'}), 500

@app.route('/consultar-vendas', methods=['GET', 'POST'])
@login_required
def consultar_vendas():
    # Filtros
    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')
    cliente_id = request.args.get('cliente_id')
    vendedor_id = request.args.get('vendedor_id')
    produto_id = request.args.get('produto_id')

    # Query base
    query = db.session.query(
        Produto.nome.label('produto_nome'),
        func.sum(ItemVenda.quantidade).label('quantidade_vendida'),
        func.sum(ItemVenda.desconto).label('desconto_total'),
        func.sum(ItemVenda.subtotal).label('total_item')
    ).join(ItemVenda.produto)
    query = query.join(ItemVenda.venda)

    # Filtros
    filtros = [Venda.excluido == False]
    if data_inicial:
        filtros.append(Venda.data_venda >= data_inicial)
    if data_final:
        filtros.append(Venda.data_venda <= data_final)
    if cliente_id:
        filtros.append(Venda.cliente_id == cliente_id)
    if vendedor_id:
        filtros.append(Venda.vendedor_id == vendedor_id)
    if produto_id:
        filtros.append(ItemVenda.produto_id == produto_id)

    query = query.filter(and_(*filtros))
    query = query.group_by(Produto.nome)
    query = query.order_by(Produto.nome)

    resultados = query.all()
    total_geral = sum([r.total_item for r in resultados]) if resultados else 0

    # Dados para os selects
    clientes = Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Cliente.nome).all()
    vendedores = Vendedor.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Vendedor.nome).all()
    produtos = Produto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Produto.nome).all()

    return render_template('consultar_vendas.html',
        resultados=resultados,
        total_geral=total_geral,
        clientes=clientes,
        vendedores=vendedores,
        produtos=produtos,
        filtros={
            'data_inicial': data_inicial,
            'data_final': data_final,
            'cliente_id': cliente_id,
            'vendedor_id': vendedor_id,
            'produto_id': produto_id
        }
    )

@app.route('/relatorio-pedidos', methods=['GET', 'POST'])
@login_required
def relatorio_pedidos():
    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')
    cliente_id = request.args.get('cliente_id')
    vendedor_id = request.args.get('vendedor_id')
    forma_pagamento = request.args.get('forma_pagamento')

    query = db.session.query(
        Venda.id.label('pedido_id'),
        Venda.numero_venda,
        func.count(ItemVenda.id).label('qtd_itens'),
        Vendedor.nome.label('vendedor_nome'),
        Cliente.nome.label('cliente_nome'),
        Venda.total,
        Venda.forma_pagamento
    ).join(Venda.vendedor).join(Venda.cliente).join(Venda.itens)

    filtros = [Venda.excluido == False]
    if data_inicial:
        filtros.append(Venda.data_venda >= data_inicial)
    if data_final:
        filtros.append(Venda.data_venda <= data_final)
    if cliente_id:
        filtros.append(Venda.cliente_id == cliente_id)
    if vendedor_id:
        filtros.append(Venda.vendedor_id == vendedor_id)
    if forma_pagamento:
        filtros.append(Venda.forma_pagamento == forma_pagamento)

    query = query.filter(and_(*filtros))
    query = query.group_by(Venda.id, Venda.numero_venda, Vendedor.nome, Cliente.nome, Venda.total, Venda.forma_pagamento)
    query = query.order_by(Venda.data_venda.desc())

    resultados = query.all()
    total_geral = sum([r.total for r in resultados]) if resultados else 0

    clientes = Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Cliente.nome).all()
    vendedores = Vendedor.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Vendedor.nome).all()
    formas_pagamento = db.session.query(Venda.forma_pagamento).distinct().all()
    formas_pagamento = [f[0] for f in formas_pagamento if f[0]]

    return render_template('relatorio_pedidos.html',
        resultados=resultados,
        total_geral=total_geral,
        clientes=clientes,
        vendedores=vendedores,
        formas_pagamento=formas_pagamento,
        filtros={
            'data_inicial': data_inicial,
            'data_final': data_final,
            'cliente_id': cliente_id,
            'vendedor_id': vendedor_id,
            'forma_pagamento': forma_pagamento
        }
    )

@app.route('/relatorio-comissao', methods=['GET', 'POST'])
@login_required
def relatorio_comissao():
    from sqlalchemy import func, and_
    from datetime import datetime, timedelta
    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')
    cliente_id = request.args.get('cliente_id')
    vendedor_id = request.args.get('vendedor_id')

    query = db.session.query(
        Venda.id.label('pedido_id'),
        Venda.numero_venda,
        Vendedor.nome.label('vendedor_nome'),
        Vendedor.comissao.label('percentual_comissao'),
        Cliente.nome.label('cliente_nome'),
        Venda.total,
        Venda.data_venda
    ).join(Venda.vendedor).join(Venda.cliente)

    filtros = [Venda.excluido == False]
    if data_inicial:
        try:
            dt_ini = datetime.strptime(data_inicial, '%Y-%m-%d')
            filtros.append(Venda.data_venda >= dt_ini)
        except:
            pass
    if data_final:
        try:
            dt_fim = datetime.strptime(data_final, '%Y-%m-%d') + timedelta(days=1)
            filtros.append(Venda.data_venda < dt_fim)
        except:
            pass
    if cliente_id:
        filtros.append(Venda.cliente_id == cliente_id)
    if vendedor_id:
        filtros.append(Venda.vendedor_id == vendedor_id)

    query = query.filter(and_(*filtros))
    query = query.order_by(Venda.data_venda.desc())

    resultados = query.all()
    # Calcular comissão de cada pedido
    pedidos = []
    total_comissao = 0
    for r in resultados:
        valor_comissao = float(r.total or 0) * float(r.percentual_comissao or 0) / 100
        pedidos.append({
            'numero_venda': r.numero_venda,
            'vendedor_nome': r.vendedor_nome,
            'cliente_nome': r.cliente_nome,
            'total': r.total,
            'data_venda': r.data_venda,
            'percentual_comissao': r.percentual_comissao,
            'valor_comissao': valor_comissao
        })
        total_comissao += valor_comissao

    clientes = Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Cliente.nome).all()
    vendedores = Vendedor.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).order_by(Vendedor.nome).all()

    return render_template('relatorio_comissao.html',
        pedidos=pedidos,
        total_comissao=total_comissao,
        clientes=clientes,
        vendedores=vendedores,
        filtros={
            'data_inicial': data_inicial,
            'data_final': data_final,
            'cliente_id': cliente_id,
            'vendedor_id': vendedor_id
        }
    )

@app.route('/relatorio-comissao/pdf')
@login_required
def relatorio_comissao_pdf():
    from sqlalchemy import func, and_
    from datetime import datetime, timedelta
    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')
    cliente_id = request.args.get('cliente_id')
    vendedor_id = request.args.get('vendedor_id')

    query = db.session.query(
        Venda.id.label('pedido_id'),
        Venda.numero_venda,
        Vendedor.nome.label('vendedor_nome'),
        Vendedor.comissao.label('percentual_comissao'),
        Cliente.nome.label('cliente_nome'),
        Venda.total,
        Venda.data_venda
    ).join(Venda.vendedor).join(Venda.cliente)

    filtros = [Venda.excluido == False]
    if not current_user.admin:
        filtros.append(Venda.usuario_cadastro == current_user.id)
    if data_inicial:
        try:
            dt_ini = datetime.strptime(data_inicial, '%Y-%m-%d')
            filtros.append(Venda.data_venda >= dt_ini)
        except:
            pass
    if data_final:
        try:
            dt_fim = datetime.strptime(data_final, '%Y-%m-%d') + timedelta(days=1)
            filtros.append(Venda.data_venda < dt_fim)
        except:
            pass
    if cliente_id:
        filtros.append(Venda.cliente_id == cliente_id)
    if vendedor_id:
        filtros.append(Venda.vendedor_id == vendedor_id)

    query = query.filter(and_(*filtros))
    query = query.order_by(Venda.data_venda.desc())

    resultados = query.all()
    pedidos = []
    total_comissao = 0
    for r in resultados:
        valor_comissao = float(r.total or 0) * float(r.percentual_comissao or 0) / 100
        pedidos.append({
            'numero_venda': r.numero_venda,
            'vendedor_nome': r.vendedor_nome,
            'cliente_nome': r.cliente_nome,
            'total': r.total,
            'data_venda': r.data_venda,
            'percentual_comissao': r.percentual_comissao,
            'valor_comissao': valor_comissao
        })
        total_comissao += valor_comissao

    rendered = render_template('pdf_relatorio_comissao.html',
        pedidos=pedidos,
        total_comissao=total_comissao,
        data_inicial=data_inicial,
        data_final=data_final
    )
    import io
    from weasyprint import HTML
    pdf_io = io.BytesIO()
    HTML(string=rendered).write_pdf(pdf_io)
    pdf_io.seek(0)
    return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name='relatorio_comissao.pdf')

@app.route('/vendas/<int:venda_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_venda(venda_id):
    venda = Venda.query.get_or_404(venda_id)
    if venda.impresso:
        flash('Esta venda já foi impressa e não pode ser editada.', 'warning')
        return redirect(url_for('vendas'))
    if request.method == 'POST':
        # Atualizar dados da venda
        venda.cliente_id = request.form.get('cliente_id')
        venda.vendedor_id = request.form.get('vendedor_id')
        venda.forma_pagamento = request.form.get('forma_pagamento')
        venda.desconto = float(request.form.get('desconto') or 0)
        venda.observacoes = request.form.get('observacoes')
        venda.tipo_parcelamento = request.form.get('tipo_parcelamento')
        venda.numero_parcelas = int(request.form.get('numero_parcelas') or 1)
        # Atualizar itens da venda
        import json
        itens_json = request.form.get('itens_json')
        if itens_json:
            # Remove itens antigos
            for item in venda.itens[:]:
                db.session.delete(item)
            db.session.flush()
            itens = json.loads(itens_json)
            subtotal = 0
            for item in itens:
                preco = float(item['preco'])
                quantidade = int(item['quantidade'])
                desconto = float(item.get('desconto', 0))
                subtotal_item = (preco * quantidade) - desconto
                subtotal += subtotal_item
                db.session.add(ItemVenda(
                    venda_id=venda.id,
                    produto_id=int(item['produto_id']),
                    quantidade=quantidade,
                    preco_unitario=preco,
                    desconto=desconto,
                    subtotal=subtotal_item,
                    brinde=item.get('brinde', ''),
                    troca=item.get('troca', '')
                ))
            venda.subtotal = subtotal
            venda.total = subtotal - venda.desconto
        db.session.commit()
        flash('Venda atualizada com sucesso!', 'success')
        return redirect(url_for('vendas'))
    clientes = Cliente.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all()
    vendedores = Vendedor.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all()
    grupos = GrupoProduto.query.filter_by(ativo=True, empresa_id=current_user.empresa_id).all()
    itens = venda.itens
    return render_template('venda_grade.html',
        clientes=clientes,
        vendedores=vendedores,
        grupos=grupos,
        venda=venda,
        itens=itens,
        edicao=True,
        data_hoje=venda.data_venda.strftime('%Y-%m-%d') if venda.data_venda else None
    )

@app.route('/usuarios', methods=['GET', 'POST'])
@login_required
def usuarios():
    if not current_user.admin:
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        acao = request.form.get('acao')
        user = User.query.get(user_id)
        if user:
            if acao == 'ativar':
                user.ativo = True
            elif acao == 'desativar':
                user.ativo = False
            elif acao == 'tornar_admin':
                user.admin = True
            elif acao == 'remover_admin':
                user.admin = False
            db.session.commit()
            flash('Permissão atualizada com sucesso!', 'success')
        return redirect(url_for('usuarios'))
    usuarios = User.query.order_by(User.nome_completo).all()
    return render_template('usuarios.html', usuarios=usuarios)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() in ['1', 'true', 'yes']
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode) 