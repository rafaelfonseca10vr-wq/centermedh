#!/usr/bin/env python3
"""
Script para configurar e testar a impressora Bluetooth Coojprt
"""

import subprocess
import sys
import os

def instalar_dependencias():
    """Instala as dependências necessárias para impressão Bluetooth"""
    print("=== INSTALANDO DEPENDÊNCIAS ===")
    
    dependencias = [
        'PyBluez==0.23',
        'python-escpos==3.0a8'
    ]
    
    for dep in dependencias:
        print(f"Instalando {dep}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✓ {dep} instalado com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"✗ Erro ao instalar {dep}: {e}")
            return False
    
    return True

def testar_bluetooth():
    """Testa se o Bluetooth está funcionando"""
    print("\n=== TESTANDO BLUETOOTH ===")
    
    try:
        import bluetooth
        print("✓ Biblioteca Bluetooth importada com sucesso!")
        
        # Testar descoberta de dispositivos
        print("Procurando dispositivos Bluetooth...")
        dispositivos = bluetooth.discover_devices(lookup_names=True, duration=5)
        
        if dispositivos:
            print(f"✓ Encontrados {len(dispositivos)} dispositivos:")
            for addr, name in dispositivos:
                print(f"  - {name} ({addr})")
        else:
            print("⚠ Nenhum dispositivo Bluetooth encontrado")
            
        return True
        
    except ImportError:
        print("✗ Biblioteca Bluetooth não encontrada!")
        return False
    except Exception as e:
        print(f"✗ Erro ao testar Bluetooth: {e}")
        return False

def testar_impressora():
    """Testa a impressora Coojprt"""
    print("\n=== TESTANDO IMPRESSORA COOJPRT ===")
    
    try:
        from config_impressora import testar_impressora
        testar_impressora()
        return True
    except Exception as e:
        print(f"✗ Erro ao testar impressora: {e}")
        return False

def main():
    """Função principal"""
    print("=== CONFIGURAÇÃO DA IMPRESSORA COOJPRT ===\n")
    
    # Verificar se estamos no Windows
    if os.name == 'nt':
        print("⚠ ATENÇÃO: No Windows, você pode precisar:")
        print("1. Instalar drivers Bluetooth")
        print("2. Habilitar Bluetooth nas configurações")
        print("3. Emparelhar a impressora manualmente primeiro")
        print()
    
    # Instalar dependências
    if not instalar_dependencias():
        print("✗ Falha ao instalar dependências!")
        return
    
    # Testar Bluetooth
    if not testar_bluetooth():
        print("✗ Problemas com Bluetooth detectados!")
        return
    
    # Testar impressora
    if not testar_impressora():
        print("✗ Problemas com impressora detectados!")
        return
    
    print("\n=== CONFIGURAÇÃO CONCLUÍDA ===")
    print("✓ Sistema de impressão configurado com sucesso!")
    print("\nPróximos passos:")
    print("1. Certifique-se de que a impressora está ligada")
    print("2. Verifique se o Bluetooth está ativo")
    print("3. Teste imprimindo um recibo pelo sistema web")

if __name__ == "__main__":
    main() 