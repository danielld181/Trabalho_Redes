#!/usr/bin/env python3
"""
Monitor de rede CORRIGIDO - captura o tráfego real das VMs
"""

import subprocess
import pandas as pd
import time
import json
from datetime import datetime
from collections import defaultdict

VM_IPS = [
    "192.168.122.10",
    "192.168.122.11",
    "192.168.122.12",
    "192.168.122.13",
    "192.168.122.14"
]

WINDOW = 5
historical_data = []
previous_interface_stats = {}

def get_active_connections_detailed():
    """Obtém conexões ativas com mais detalhes."""
    connections = defaultdict(lambda: {
        'tcp_established': 0,
        'tcp_listening': 0,
        'udp_connections': 0,
        'total_connections': 0,
        'connection_details': []
    })

    try:
        # Usa ss com mais opções para capturar conexões estabelecidas
        result = subprocess.run(['ss', '-tun', 'state', 'all'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            result = subprocess.run(['ss', '-tun'], capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                parts = line.split()
                if len(parts) >= 5:
                    proto = parts[0].lower()
                    state = parts[1] if len(parts) > 5 else ""
                    local_addr = parts[4] if len(parts) > 4 else parts[3]
                    remote_addr = parts[5] if len(parts) > 5 else ""

                    # Extrai IPs
                    for vm_ip in VM_IPS:
                        if vm_ip in local_addr or vm_ip in remote_addr:
                            if 'tcp' in proto:
                                if 'ESTAB' in state:
                                    connections[vm_ip]['tcp_established'] += 1
                                elif 'LISTEN' in state:
                                    connections[vm_ip]['tcp_listening'] += 1
                                connections[vm_ip]['total_connections'] += 1
                            elif 'udp' in proto:
                                connections[vm_ip]['udp_connections'] += 1
                                connections[vm_ip]['total_connections'] += 1

                            # Salva detalhes
                            connections[vm_ip]['connection_details'].append({
                                'protocol': proto,
                                'state': state,
                                'local': local_addr,
                                'remote': remote_addr
                            })
                            break

    except Exception as e:
        print(f"Erro obtendo conexões: {e}")

    return connections

def get_interface_traffic_delta():
    """Calcula delta de tráfego das interfaces entre medições."""
    global previous_interface_stats

    current_stats = {}
    traffic_delta = {}

    try:
        with open('/proc/net/dev', 'r') as f:
            lines = f.readlines()[2:]  # Skip headers

        for line in lines:
            if ':' in line:
                parts = line.split()
                interface = parts[0].rstrip(':')

                if len(parts) >= 17:
                    current_stats[interface] = {
                        'rx_bytes': int(parts[1]),
                        'rx_packets': int(parts[2]),
                        'tx_bytes': int(parts[9]),
                        'tx_packets': int(parts[10])
                    }

        # Calcula delta se temos dados anteriores
        if previous_interface_stats:
            for interface, current in current_stats.items():
                if interface in previous_interface_stats:
                    prev = previous_interface_stats[interface]
                    traffic_delta[interface] = {
                        'rx_bytes_delta': current['rx_bytes'] - prev['rx_bytes'],
                        'tx_bytes_delta': current['tx_bytes'] - prev['tx_bytes'],
                        'rx_packets_delta': current['rx_packets'] - prev['rx_packets'],
                        'tx_packets_delta': current['tx_packets'] - prev['tx_packets']
                    }

        previous_interface_stats = current_stats.copy()

    except Exception as e:
        print(f"Erro calculando delta de tráfego: {e}")

    return traffic_delta, current_stats

def test_vm_services_detailed():
    """Testa serviços com mais detalhes."""
    services = {}

    for vm_ip in VM_IPS:
        services[vm_ip] = {
            'http_response_time': 0,
            'http_status': 0,
            'http_bytes': 0,
            'ssh_open': False,
            'ftp_open': False,
            'ping_time': 0
        }

        # Teste HTTP com timing
        try:
            import requests
            start_time = time.time()
            response = requests.get(f"http://{vm_ip}", timeout=3)
            response_time = (time.time() - start_time) * 1000

            services[vm_ip]['http_response_time'] = response_time
            services[vm_ip]['http_status'] = response.status_code
            services[vm_ip]['http_bytes'] = len(response.content)

        except Exception as e:
            services[vm_ip]['http_response_time'] = 0

        # Teste SSH
        try:
            result = subprocess.run(['nc', '-z', '-w', '1', vm_ip, '22'],
                                  capture_output=True, timeout=2)
            services[vm_ip]['ssh_open'] = result.returncode == 0
        except:
            services[vm_ip]['ssh_open'] = False

        # Teste FTP
        try:
            result = subprocess.run(['nc', '-z', '-w', '1', vm_ip, '21'],
                                  capture_output=True, timeout=2)
            services[vm_ip]['ftp_open'] = result.returncode == 0
        except:
            services[vm_ip]['ftp_open'] = False

        # Ping com timing - DEBUG MELHORADO
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '2', vm_ip],
                                  capture_output=True, text=True, timeout=4)

            # DEBUG: mostra saída completa
            if result.returncode == 0:
                print(f"DEBUG PING {vm_ip}: SUCCESS - {result.stdout.strip()}")
                for line in result.stdout.split('\n'):
                    if 'time=' in line:
                        try:
                            time_part = line.split('time=')[1].split()[0]
                            # Remove 'ms' e CONVERTE VÍRGULA PARA PONTO
                            ping_time = float(time_part.replace('ms', '').replace(',', '.'))
                            services[vm_ip]['ping_time'] = ping_time
                            break
                        except Exception as parse_error:
                            print(f"DEBUG PING {vm_ip}: Parse error - {parse_error}")
                            services[vm_ip]['ping_time'] = 0.1  # Marca como online mas com erro de parse
            else:
                print(f"DEBUG PING {vm_ip}: FAILED - Return code: {result.returncode}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                services[vm_ip]['ping_time'] = 0

        except Exception as e:
            print(f"DEBUG PING {vm_ip}: EXCEPTION - {e}")
            services[vm_ip]['ping_time'] = 0

    return services

def collect_window_data():
    """Coleta dados melhorados para uma janela de tempo."""
    timestamp = datetime.now()

    print(f"\n{'='*70}")
    print(f"COLETA DETALHADA {timestamp.strftime('%H:%M:%S')} - Janela de {WINDOW}s")
    print(f"{'='*70}")

    # Coleta métricas avançadas
    connections = get_active_connections_detailed()
    traffic_delta, interface_stats = get_interface_traffic_delta()
    services = test_vm_services_detailed()

    window_data = []

    for vm_ip in VM_IPS:
        conn_data = connections[vm_ip]
        service_data = services[vm_ip]

        data = {
            'timestamp': timestamp,
            'vm_ip': vm_ip,
            'ping_time_ms': service_data['ping_time'],
            'ping_ok': service_data['ping_time'] > 0,

            # Conexões detalhadas
            'tcp_established': conn_data['tcp_established'],
            'tcp_listening': conn_data['tcp_listening'],
            'udp_connections': conn_data['udp_connections'],
            'total_connections': conn_data['total_connections'],

            # Serviços detalhados
            'http_status': service_data['http_status'],
            'http_response_time_ms': service_data['http_response_time'],
            'http_bytes_received': service_data['http_bytes'],
            'ssh_service': service_data['ssh_open'],
            'ftp_service': service_data['ftp_open'],

            # Tráfego de interface (soma das vnet para a VM)
            'interface_rx_bytes_delta': 0,
            'interface_tx_bytes_delta': 0,
            'interface_rx_packets_delta': 0,
            'interface_tx_packets_delta': 0
        }

        window_data.append(data)
        historical_data.append(data)

        # Status visual melhorado
        status_parts = []

        if data['ping_ok']:
            status_parts.append(f"🟢 {data['ping_time_ms']:.1f}ms")
        else:
            status_parts.append("🔴 Offline")

        # Serviços
        service_icons = []
        if service_data['http_status'] == 200:
            service_icons.append(f"🌐HTTP({service_data['http_response_time']:.0f}ms)")
        if service_data['ssh_open']:
            service_icons.append("🔐SSH")
        if service_data['ftp_open']:
            service_icons.append("📁FTP")

        if service_icons:
            status_parts.append(" ".join(service_icons))

        # Conexões
        if data['total_connections'] > 0:
            conn_detail = f"🔗{data['total_connections']}conn"
            if data['tcp_established'] > 0:
                conn_detail += f"(EST:{data['tcp_established']})"
            status_parts.append(conn_detail)

        status = " | ".join(status_parts)
        print(f"🖥️  {vm_ip}: {status}")

    # Mostra tráfego de interfaces VM
    print(f"\n📊 Tráfego nas interfaces VM (últimos {WINDOW}s):")
    vm_interfaces = ['virbr0', 'vnet1', 'vnet2', 'vnet3', 'vnet4', 'vnet5']
    total_rx_delta = 0
    total_tx_delta = 0

    for interface in vm_interfaces:
        if interface in traffic_delta:
            delta = traffic_delta[interface]
            rx_kb = delta['rx_bytes_delta'] / 1024
            tx_kb = delta['tx_bytes_delta'] / 1024

            if rx_kb > 0 or tx_kb > 0:
                print(f"   {interface}: RX=+{rx_kb:.1f}KB TX=+{tx_kb:.1f}KB ({delta['rx_packets_delta']}↓ {delta['tx_packets_delta']}↑ pkts)")
                total_rx_delta += delta['rx_bytes_delta']
                total_tx_delta += delta['tx_bytes_delta']

    if total_rx_delta > 0 or total_tx_delta > 0:
        print(f"   TOTAL DELTA: RX=+{total_rx_delta/1024:.1f}KB TX=+{total_tx_delta/1024:.1f}KB")
    else:
        print("   Nenhum tráfego detectado nesta janela")

    return window_data

def save_to_excel():
    """Salva dados melhorados em Excel."""
    if not historical_data:
        print("❌ Nenhum dado para salvar")
        return

    try:
        df = pd.DataFrame(historical_data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"vm_traffic_analysis_{timestamp}.xlsx"

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Dados brutos
            df.to_excel(writer, sheet_name='Dados_Brutos', index=False)

            # Resumo por VM com mais métricas
            summary = df.groupby('vm_ip').agg({
                'ping_ok': 'mean',
                'ping_time_ms': 'mean',
                'total_connections': ['sum', 'mean', 'max'],
                'tcp_established': 'sum',
                'http_status': lambda x: (x == 200).mean(),
                'http_response_time_ms': 'mean',
                'http_bytes_received': 'sum',
                'ssh_service': 'mean',
                'ftp_service': 'mean'
            }).round(3)
            summary.to_excel(writer, sheet_name='Resumo_Detalhado')

            # Análise de performance
            performance = df[df['ping_ok'] == True].groupby('vm_ip').agg({
                'ping_time_ms': ['min', 'max', 'mean', 'std'],
                'http_response_time_ms': ['min', 'max', 'mean', 'std']
            }).round(3)
            performance.to_excel(writer, sheet_name='Performance_VMs')

            # Timeline detalhada
            timeline = df[['timestamp', 'vm_ip', 'ping_time_ms', 'total_connections',
                          'http_response_time_ms', 'http_status']].tail(100)
            timeline.to_excel(writer, sheet_name='Timeline_Detalhada', index=False)

            # Estatísticas gerais
            stats = {
                'Total de Medições': len(df),
                'Período de Coleta': f"{df['timestamp'].min()} até {df['timestamp'].max()}",
                'VMs Online (média)': f"{df['ping_ok'].mean()*100:.1f}%",
                'Tempo médio de ping': f"{df[df['ping_ok']]['ping_time_ms'].mean():.2f}ms",
                'Conexões TCP estabelecidas': df['tcp_established'].sum(),
                'Total de conexões': df['total_connections'].sum(),
                'Requisições HTTP bem-sucedidas': f"{(df['http_status'] == 200).mean()*100:.1f}%",
                'Tempo médio HTTP': f"{df[df['http_status'] == 200]['http_response_time_ms'].mean():.2f}ms",
                'Total bytes HTTP recebidos': df['http_bytes_received'].sum(),
                'Serviços SSH ativos': f"{df['ssh_service'].mean()*100:.1f}%",
                'Serviços FTP ativos': f"{df['ftp_service'].mean()*100:.1f}%"
            }

            stats_df = pd.DataFrame(list(stats.items()), columns=['Métrica', 'Valor'])
            stats_df.to_excel(writer, sheet_name='Estatisticas_Completas', index=False)

        print(f"💾 Dados salvos: {filename}")
        print(f"📊 Registros: {len(df)} | VMs ativas: {df['ping_ok'].sum()}/{len(df)}")

    except Exception as e:
        print(f"❌ Erro salvando Excel: {e}")

def main():
    """Função principal."""
    print("🚀 MONITOR DE REDE CORRIGIDO - CAPTURA TRÁFEGO REAL")
    print(f"{'='*70}")
    print(f"🎯 VMs: {VM_IPS}")
    print(f"⏱️  Janela: {WINDOW}s")
    print(f"📡 Interfaces VM: virbr0, vnet1-5")
    print(f"🔧 Métricas: conexões, latência, throughput, serviços")
    print(f"💾 Saída: Excel detalhado")
    print(f"{'='*70}")

    try:
        while True:
            window_data = collect_window_data()

            # Mostra resumo da janela
            online_vms = sum(1 for d in window_data if d['ping_ok'])
            total_connections = sum(d['total_connections'] for d in window_data)
            total_http_requests = sum(1 for d in window_data if d['http_status'] == 200)

            print(f"\n📈 RESUMO JANELA:")
            print(f"   🟢 {online_vms}/{len(VM_IPS)} VMs online")
            print(f"   🔗 {total_connections} conexões ativas")
            print(f"   🌐 {total_http_requests} requisições HTTP OK")

            # Salva a cada 6 janelas (30 segundos)
            if len(historical_data) % (len(VM_IPS) * 6) == 0:
                save_to_excel()

            print(f"⏳ Próxima coleta em {WINDOW}s...")
            time.sleep(WINDOW)

    except KeyboardInterrupt:
        print("\n\n⏹️  Monitor interrompido")
        if historical_data:
            save_to_excel()
            print("📊 Dados finais salvos com sucesso!")

if __name__ == "__main__":
    main()
