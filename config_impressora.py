#!/usr/bin/env python3
"""
Configuração da Impressora Bluetooth Coojprt
"""

import bluetooth
import time
import serial

class ImpressoraCoojprt:
    def __init__(self, mac_address="86:67:7A:48:0A:83", porta_serial="COM10"):
        """
        Inicializa a impressora Coojprt
        
        Args:
            mac_address (str): Endereço MAC da impressora (ex: "00:11:22:33:44:55")
        """
        self.mac_address = mac_address
        self.porta_serial = porta_serial
        self.socket = None
        
    def descobrir_impressoras(self):
        """Descobre impressoras Bluetooth disponíveis"""
        print("Procurando dispositivos Bluetooth...")
        dispositivos = bluetooth.discover_devices(lookup_names=True)
        
        print(f"\n📱 Dispositivos Bluetooth encontrados ({len(dispositivos)}):")
        for addr, name in dispositivos:
            print(f"   - {name} ({addr})")
        
        impressoras = []
        for addr, name in dispositivos:
            # Procurar por diferentes nomes de impressoras
            if any(keyword in name.lower() for keyword in ['coojprt', 'printer', 'print', 'impressora', 'thermal']):
                impressoras.append({
                    'mac': addr,
                    'nome': name
                })
                print(f"\n✅ Impressora encontrada: {name} ({addr})")
        
        if not impressoras:
            print("\n⚠️ Nenhuma impressora identificada automaticamente.")
            print("💡 Dica: Verifique se a impressora está ligada e no modo de emparelhamento.")
            print("💡 Dica: Se sua impressora tem outro nome, você pode configurar manualmente.")
        
        return impressoras
    
    def conectar(self, mac_address=None):
        """Conecta à impressora"""
        if mac_address:
            self.mac_address = mac_address
            
        if not self.mac_address:
            raise ValueError("Endereço MAC da impressora não especificado")
            
        try:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((self.mac_address, 1))
            print(f"Conectado à impressora {self.mac_address}")
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False
    
    def desconectar(self):
        """Desconecta da impressora"""
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def imprimir_texto(self, texto):
        """Imprime texto na impressora"""
        if not self.socket:
            raise Exception("Não conectado à impressora")
            
        try:
            # Adicionar comandos de formatação para Coojprt
            comandos = [
                b'\x1B\x40',  # Initialize printer
                b'\x1B\x61\x01',  # Center alignment
                b'\x1B\x21\x10',  # Double height and width
            ]
            
            # Enviar comandos de inicialização
            for comando in comandos:
                self.socket.send(comando)
                time.sleep(0.1)
            
            # Enviar texto
            self.socket.send(texto.encode('utf-8'))
            
            # Comandos finais
            self.socket.send(b'\n\n\n\n')  # Feed paper
            self.socket.send(b'\x1B\x69')  # Cut paper
            
            print("Texto enviado para impressora com sucesso!")
            return True
            
        except Exception as e:
            print(f"Erro ao imprimir: {e}")
            return False
    
    def imprimir_recibo(self, dados_recibo):
        """Imprime recibo formatado"""
        recibo = f"""
========================================
         RECIBO DE PAGAMENTO
========================================

Data: {dados_recibo['data']}
Recibo Nº: {dados_recibo['numero']:06d}

========================================
CLIENTE:
Nome: {dados_recibo['cliente_nome']}
CPF: {dados_recibo['cliente_cpf']}

VENDA:
Número: {dados_recibo['venda_numero']}
Parcela: {dados_recibo['parcela']}/{dados_recibo['total_parcelas']}

========================================
VALOR PAGO: R$ {dados_recibo['valor']:.2f}
========================================

Vendedor: {dados_recibo['vendedor']}

========================================
Assinatura: _________________
========================================

"""
        return self.imprimir_texto(recibo)

    def imprimir_via_serial(self, texto):
        """Imprime texto diretamente na porta serial COM10"""
        try:
            with serial.Serial(self.porta_serial, 9600, timeout=1) as ser:
                # Comandos de inicialização (opcional)
                ser.write(b'\x1B\x40')  # Inicializa impressora
                time.sleep(0.1)
                ser.write(texto.encode('utf-8'))
                ser.write(b'\n\n\n\n')  # Alimenta papel
                ser.write(b'\x1B\x69')   # Corta papel (se suportado)
                return True
        except Exception as e:
            print(f"Erro ao imprimir via serial: {e}")
            return False

    def imprimir_recibo_serial(self, dados_recibo):
        recibo = f"""
========================================
         RECIBO DE PAGAMENTO
========================================

Data: {dados_recibo['data']}
Recibo Nº: {dados_recibo['numero']:06d}

========================================
CLIENTE:
Nome: {dados_recibo['cliente_nome']}
CPF: {dados_recibo['cliente_cpf']}

VENDA:
Número: {dados_recibo['venda_numero']}
Parcela: {dados_recibo['parcela']}/{dados_recibo['total_parcelas']}

========================================
VALOR PAGO: R$ {dados_recibo['valor']:.2f}
========================================

Vendedor: {dados_recibo['vendedor']}

========================================
Assinatura: _________________
========================================

"""
        return self.imprimir_via_serial(recibo)

def testar_impressora():
    """Função para testar a conexão com a impressora"""
    impressora = ImpressoraCoojprt()
    
    print("=== TESTE DE IMPRESSORA COOJPRT ===")
    
    # Descobrir impressoras
    impressoras = impressora.descobrir_impressoras()
    
    if not impressoras:
        print("Nenhuma impressora Coojprt encontrada!")
        return
    
    # Usar a primeira impressora encontrada
    mac = impressoras[0]['mac']
    print(f"Tentando conectar à: {impressoras[0]['nome']} ({mac})")
    
    # Conectar
    if impressora.conectar(mac):
        # Teste de impressão
        dados_teste = {
            'data': '01/01/2024 10:00',
            'numero': 1,
            'cliente_nome': 'CLIENTE TESTE',
            'cliente_cpf': '000.000.000-00',
            'venda_numero': '1',
            'parcela': 1,
            'total_parcelas': 3,
            'valor': 100.00,
            'vendedor': 'VENDEDOR TESTE'
        }
        
        if impressora.imprimir_recibo(dados_teste):
            print("Teste de impressão realizado com sucesso!")
        else:
            print("Erro no teste de impressão!")
        
        impressora.desconectar()
    else:
        print("Falha ao conectar com a impressora!")

if __name__ == "__main__":
    testar_impressora() 