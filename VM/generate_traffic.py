#!/usr/bin/env python3
"""
Gerador de tráfego melhorado que mantém conexões ativas
"""

import requests
import socket
import subprocess
import time
import threading
from datetime import datetime

VM_IPS = ["192.168.122.10", "192.168.122.11", "192.168.122.12", "192.168.122.13", "192.168.122.14"]

def create_persistent_connections():
    """Cria conexões TCP persistentes."""
    print("🔗 Criando conexões TCP persistentes...")

    connections = []
    for vm_ip in VM_IPS:
        try:
            # Conexão HTTP Keep-Alive
            session = requests.Session()
            session.headers.update({'Connection': 'keep-alive'})

            response = session.get(f"http://{vm_ip}", timeout=5)
            if response.status_code == 200:
                connections.append((vm_ip, session))
                print(f"   ✅ Conexão persistente com {vm_ip}")
            else:
                print(f"   ❌ Falha HTTP para {vm_ip}: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Erro conectando {vm_ip}: {e}")

    return connections

def generate_continuous_traffic():
    """Gera tráfego contínuo."""
    print("📡 Iniciando geração contínua de tráfego...")

    cycle = 0

    try:
        while True:
            cycle += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n🔄 CICLO {cycle} - {timestamp}")

            for vm_ip in VM_IPS:
                # HTTP requests múltiplas
                for endpoint in ['/', '/test.html', '/data.json']:
                    try:
                        response = requests.get(f"http://{vm_ip}{endpoint}", timeout=2)
                        print(f"   HTTP {vm_ip}{endpoint}: {response.status_code}")
                    except requests.exceptions.ConnectException:
                        print(f"   HTTP {vm_ip}{endpoint}: Conexão recusada (serviço inativo)")
                    except Exception as e:
                        print(f"   HTTP {vm_ip}{endpoint}: {str(e)[:30]}...")

                # Conexões TCP diretas
                for port, service in [(80, 'HTTP'), (22, 'SSH'), (21, 'FTP')]:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        result = sock.connect_ex((vm_ip, port))

                        if result == 0:
                            # Mantém conexão aberta por um tempo
                            if port == 80:
                                sock.send(b"GET / HTTP/1.1\r\nHost: " + vm_ip.encode() + b"\r\n\r\n")
                                data = sock.recv(1024)
                                print(f"   TCP {vm_ip}:{port} ({service}): ✅ {len(data)} bytes")
                            else:
                                print(f"   TCP {vm_ip}:{port} ({service}): ✅ Conectado")

                            time.sleep(0.5)  # Mantém conexão aberta
                        else:
                            print(f"   TCP {vm_ip}:{port} ({service}): ❌ Recusado")

                        sock.close()

                    except Exception as e:
                        print(f"   TCP {vm_ip}:{port} ({service}): ❌ {str(e)[:20]}...")

                # Ping contínuo
                try:
                    result = subprocess.run(['ping', '-c', '1', vm_ip],
                                          capture_output=True, timeout=3)
                    if result.returncode == 0:
                        print(f"   PING {vm_ip}: ✅")
                    else:
                        print(f"   PING {vm_ip}: ❌")
                except:
                    print(f"   PING {vm_ip}: ❌ Timeout")

            print(f"✅ Ciclo {cycle} completo - aguardando 3 segundos...")
            time.sleep(3)

    except KeyboardInterrupt:
        print(f"\n⏹️  Gerador interrompido após {cycle} ciclos")

def background_ping_flood():
    """Ping contínuo em background."""
    def ping_vm(vm_ip):
        while True:
            try:
                subprocess.run(['ping', '-c', '1', vm_ip], capture_output=True, timeout=2)
                time.sleep(2)
            except:
                time.sleep(5)

    print("🏓 Iniciando ping contínuo em background...")
    for vm_ip in VM_IPS:
        thread = threading.Thread(target=ping_vm, args=(vm_ip,))
        thread.daemon = True
        thread.start()

def main():
    """Função principal."""
    print("🚀 GERADOR DE TRÁFEGO MELHORADO")
    print("="*50)
    print(f"🎯 VMs: {VM_IPS}")
    print("🔗 Criando conexões persistentes...")
    print("📡 Gerando tráfego contínuo...")
    print("="*50)

    # Inicia ping em background
    background_ping_flood()

    # Gera tráfego principal
    generate_continuous_traffic()

if __name__ == "__main__":
    main()
