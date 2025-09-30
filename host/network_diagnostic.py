#!/usr/bin/env python3
"""
Script de diagnóstico para identificar o problema
"""

import subprocess
import requests
import socket
import time

VM_IPS = ["192.168.122.10", "192.168.122.11", "192.168.122.12", "192.168.122.13", "192.168.122.14"]

def test_vm_services():
    """Testa se as VMs têm serviços configurados."""
    print("🔍 TESTE 1: Verificando serviços nas VMs")
    print("="*50)

    for vm_ip in VM_IPS:
        print(f"\n🖥️  Testando {vm_ip}:")

        # Teste HTTP
        try:
            response = requests.get(f"http://{vm_ip}", timeout=3)
            print(f"   ✅ HTTP: {response.status_code} - {len(response.content)} bytes")
        except Exception as e:
            print(f"   ❌ HTTP: {str(e)[:50]}...")

        # Teste portas TCP
        for port, service in [(22, 'SSH'), (80, 'HTTP'), (21, 'FTP')]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((vm_ip, port))
                sock.close()

                if result == 0:
                    print(f"   ✅ {service} (porta {port}): Aberta")
                else:
                    print(f"   ❌ {service} (porta {port}): Fechada")
            except Exception as e:
                print(f"   ❌ {service} (porta {port}): Erro - {e}")

def check_active_connections():
    """Verifica conexões ativas no sistema."""
    print(f"\n🔍 TESTE 2: Conexões ativas no sistema")
    print("="*50)

    try:
        # ss command
        result = subprocess.run(['ss', '-tuln'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            vm_connections = []

            for line in lines:
                for vm_ip in VM_IPS:
                    if vm_ip in line:
                        vm_connections.append(line.strip())

            if vm_connections:
                print("📡 Conexões relacionadas às VMs encontradas:")
                for conn in vm_connections[:10]:  # Mostra até 10
                    print(f"   {conn}")
            else:
                print("❌ Nenhuma conexão relacionada às VMs encontrada")

                # Mostra algumas conexões gerais
                print("\n📋 Algumas conexões ativas do sistema:")
                active_lines = [line for line in lines if 'LISTEN' in line or 'ESTAB' in line]
                for line in active_lines[:5]:
                    print(f"   {line.strip()}")
        else:
            print("❌ Erro executando comando ss")

    except Exception as e:
        print(f"❌ Erro verificando conexões: {e}")

def test_interface_traffic():
    """Verifica tráfego nas interfaces de rede."""
    print(f"\n🔍 TESTE 3: Tráfego nas interfaces")
    print("="*50)

    try:
        with open('/proc/net/dev', 'r') as f:
            lines = f.readlines()[2:]  # Skip headers

        print("📊 Estatísticas das interfaces:")
        for line in lines:
            if ':' in line:
                parts = line.split()
                interface = parts[0].rstrip(':')

                if len(parts) >= 17:
                    rx_bytes = int(parts[1])
                    rx_packets = int(parts[2])
                    tx_bytes = int(parts[9])
                    tx_packets = int(parts[10])

                    # Mostra interfaces relevantes
                    if any(x in interface for x in ['vnet', 'virbr', 'enp', 'eth', 'wlan']):
                        rx_mb = rx_bytes / 1024 / 1024
                        tx_mb = tx_bytes / 1024 / 1024
                        print(f"   {interface:10}: RX={rx_mb:8.1f}MB/{rx_packets:6}pkts | TX={tx_mb:8.1f}MB/{tx_packets:6}pkts")

    except Exception as e:
        print(f"❌ Erro lendo /proc/net/dev: {e}")

def monitor_real_time_connections():
    """Monitora conexões em tempo real."""
    print(f"\n🔍 TESTE 4: Monitor em tempo real (10 segundos)")
    print("="*50)
    print("Gerando tráfego e monitorando conexões...")

    for i in range(10):
        print(f"\n⏱️  Segundo {i+1}/10:")

        # Gera tráfego
        for vm_ip in VM_IPS[:2]:  # Testa apenas 2 VMs para ser mais rápido
            try:
                requests.get(f"http://{vm_ip}", timeout=1)
                print(f"   📤 HTTP request para {vm_ip}")
            except:
                print(f"   ❌ HTTP falhou para {vm_ip}")

        # Verifica conexões imediatamente
        try:
            result = subprocess.run(['ss', '-tun'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                vm_connections = 0
                for line in result.stdout.split('\n'):
                    for vm_ip in VM_IPS:
                        if vm_ip in line:
                            vm_connections += 1
                            break

                print(f"   📡 Conexões ativas com VMs: {vm_connections}")
            else:
                print("   ❌ Erro verificando conexões")
        except:
            print("   ❌ Timeout verificando conexões")

        time.sleep(1)

def check_vm_routing():
    """Verifica roteamento para as VMs."""
    print(f"\n🔍 TESTE 5: Roteamento e configuração de rede")
    print("="*50)

    for vm_ip in VM_IPS[:2]:  # Testa apenas 2 para ser mais rápido
        print(f"\n🖥️  Analisando rota para {vm_ip}:")

        try:
            # Verifica rota
            result = subprocess.run(['ip', 'route', 'get', vm_ip], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                print(f"   📍 Rota: {result.stdout.strip()}")
            else:
                print("   ❌ Erro obtendo rota")

            # Traceroute simples
            result = subprocess.run(['ping', '-c', '1', vm_ip], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'time=' in line:
                        print(f"   ⏱️  Ping: {line.strip()}")
                        break
            else:
                print("   ❌ Ping falhou")

        except Exception as e:
            print(f"   ❌ Erro: {e}")

def main():
    """Executa todos os testes de diagnóstico."""
    print("🔍 DIAGNÓSTICO COMPLETO DA REDE")
    print("="*60)
    print("Investigando por que não há tráfego capturado...")
    print("="*60)

    test_vm_services()
    check_active_connections()
    test_interface_traffic()
    monitor_real_time_connections()
    check_vm_routing()

    print(f"\n📋 CONCLUSÕES:")
    print("="*50)
    print("1. Se HTTP falha → VMs não têm Apache configurado")
    print("2. Se portas fechadas → Serviços não instalados")
    print("3. Se sem conexões ativas → Monitor não vê o tráfego")
    print("4. Se interfaces com tráfego zero → Interface errada")
    print("5. Execute este diagnóstico enquanto gera tráfego!")

if __name__ == "__main__":
    main()
