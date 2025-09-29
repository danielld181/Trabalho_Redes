# Dashboard de Análise de Tráfego de Servidor em Tempo Real

## 📋 Visão Geral

Este projeto implementa um sistema de monitoramento de tráfego de rede em tempo real que captura, processa e visualiza dados de comunicação entre um servidor-alvo e múltiplos clientes. O sistema utiliza janelas de tempo de 5 segundos para agregar dados de tráfego e permite análise detalhada (drill-down) por protocolo.

## 🏗️ Arquitetura do Sistema

### Componentes Principais:
- **Monitor de Captura**: Coleta dados de tráfego de rede
- **Sistema de Agregação**: Processa dados em janelas temporais
- **API REST**: Serve dados em formato JSON
- **Interface Web**: Dashboard interativo com gráficos
- **Gerador de Tráfego**: Simula atividade de rede para testes

### Tecnologias Utilizadas:
- **Backend**: Python 3 com Scapy, Pandas
- **Monitoramento**: Análise de interfaces de rede e conexões TCP/UDP
- **Dados**: Export para Excel com múltiplas planilhas
- **Ambiente**: NixOS com ambiente isolado

## 🚀 Configuração do Ambiente

### Pré-requisitos

1. **Sistema NixOS** ou ambiente compatível
2. **Permissões de administrador** para captura de pacotes
3. **Máquinas virtuais** para simulação de tráfego

### Instalação

1. **Clone o repositório e acesse o diretório**
```bash
cd traffic-dashboard
```

2. **Configure o ambiente NixOS**
```bash
nix-shell shell.nix
```

3. **Configure permissões de rede**
```bash
chmod +x setup_capabilities.sh
./setup_capabilities.sh
```

### Configuração das VMs de Teste

Execute o script de configuração em cada VM Ubuntu:

```bash
chmod +x ubuntu_vm_setup.sh
./ubuntu_vm_setup.sh
```

Este script irá:
- Instalar Apache2, FTP e SSH
- Configurar páginas web de teste
- Criar endpoints para simulação de tráfego
- Inicializar todos os serviços

## 🔧 Configuração do Projeto

### 1. Definir IPs das VMs

Edite o arquivo `traffic_analyzer_excel.py` e configure os IPs das suas VMs:

```python
VM_IPS = [
    "192.168.122.10",
    "192.168.122.11", 
    "192.168.122.12",
    "192.168.122.13",
    "192.168.122.14"
]
```

### 2. Validar Conectividade

Execute o diagnóstico de rede:

```bash
python3 network_diagnostic.py
```

Verifique se:
- ✅ VMs respondem ao ping
- ✅ Serviços HTTP/SSH/FTP estão ativos
- ✅ Conexões de rede são detectadas

## ▶️ Execução do Sistema

### 1. Iniciar o Monitor (Terminal 1)

```bash
sudo python3 traffic_analyzer_excel.py
```

**Saída esperada:**
```
🚀 MONITOR DE REDE CORRIGIDO - CAPTURA TRÁFEGO REAL
======================================================================
🎯 VMs: ['192.168.122.10', '192.168.122.11', ...]
⏱️ Janela: 5s
🔗 Interfaces VM: virbr0, vnet1-5
🔧 Métricas: conexões, latência, throughput, serviços
💾 Saída: Excel detalhado
======================================================================
```

### 2. Gerar Tráfego de Teste (Terminal 2)

```bash
python3 generate_traffic.py
```

**O gerador irá:**
- Criar conexões HTTP persistentes
- Estabelecer conexões TCP em múltiplas portas
- Executar pings contínuos
- Simular carga realista de rede

### 3. Monitorar Resultados

O sistema exibirá em tempo real:

```
COLETA DETALHADA 14:23:15 - Janela de 5s
======================================================================
🖥️ 192.168.122.10: 🟢 12.3ms | 🌐HTTP(45ms) 📗SSH | 🔗3conn(EST:1)
🖥️ 192.168.122.11: 🟢 8.7ms | 🌐HTTP(32ms) 📗SSH | 🔗2conn(EST:1)
...

📊 Tráfego nas interfaces VM (últimos 5s):
   virbr0: RX=+2.3KB TX=+1.8KB (23↓ 18↑ pkts)
   vnet1: RX=+0.8KB TX=+0.5KB (8↓ 5↑ pkts)
   
📈 RESUMO JANELA:
   🟢 5/5 VMs online
   🔗 12 conexões ativas  
   🌐 5 requisições HTTP OK
```

## 📊 Análise de Dados

### Arquivo Excel Gerado

O sistema salva automaticamente dados em Excel com as seguintes abas:

1. **Dados_Brutos**: Todas as métricas coletadas
2. **Resumo_Detalhado**: Agregações por VM
3. **Performance_VMs**: Estatísticas de latência e tempo de resposta
4. **Timeline_Detalhada**: Últimas 100 medições
5. **Estatisticas_Completas**: Métricas gerais do monitoramento

### Métricas Capturadas

- **Conectividade**: Ping, latência, disponibilidade
- **Conexões**: TCP estabelecidas, UDP, portas de escuta
- **Serviços**: HTTP, SSH, FTP (status e tempo de resposta)
- **Tráfego**: Bytes e pacotes por interface de rede
- **Performance**: Tempos de resposta e throughput

## 🔍 Análise e Drill-Down

### Visualização por Cliente
- Volume de tráfego agregado por IP de origem
- Janelas de 5 segundos com dados históricos
- Identificação de clientes mais ativos

### Drill-Down por Protocolo
- Visualização detalhada por protocolo (HTTP, SSH, FTP, ICMP)
- Análise de padrões de comunicação

### Métricas em Tempo Real
- Atualização automática a cada 5 segundos
- Detecção de anomalias de tráfego
- Monitoramento de disponibilidade de serviços

## 🧪 Testes e Validação

### Cenários de Teste

1. **Teste Básico**
   ```bash
   # Terminal 1: Monitor
   sudo python3 traffic_analyzer_excel.py
   
   # Terminal 2: Tráfego simples
   curl http://192.168.122.10
   ping -c 5 192.168.122.11
   ```

2. **Teste de Carga**
   ```bash
   # Gerador contínuo
   python3 generate_traffic.py
   ```

3. **Teste de Conectividade**
   ```bash
   # Diagnóstico completo
   python3 network_diagnostic.py
   ```

### Validação dos Resultados

- ✅ VMs respondem consistentemente ao ping
- ✅ Conexões TCP são estabelecidas e monitoradas
- ✅ Tráfego HTTP é capturado e medido
- ✅ Dados são salvos corretamente no Excel
- ✅ Interface mostra métricas em tempo real

## 🔧 Troubleshooting

### Problemas Comuns

1. **Sem permissões de rede**
   ```bash
   sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)
   # ou execute com sudo
   ```

2. **VMs não respondem**
   ```bash
   # Verifique conectividade
   python3 network_diagnostic.py
   
   # Configure serviços nas VMs
   ./ubuntu_vm_setup.sh
   ```

3. **Nenhum tráfego capturado**
   ```bash
   # Verifique interfaces ativas
   ip addr show
   
   # Force geração de tráfego
   python3 generate_traffic.py
   ```

4. **Erro de dependências**
   ```bash
   # Reinstale ambiente NixOS
   nix-shell shell.nix
   ```

### Debug Avançado

```bash
# Monitore conexões em tempo real
watch -n 1 'ss -tuln | grep -E "(192.168.122|:80|:22|:21)"'

# Verifique tráfego de interface
watch -n 1 'cat /proc/net/dev | grep -E "(vnet|virbr)"'

# Teste individual de VMs
for ip in 192.168.122.{10..14}; do 
  echo "Testando $ip:"; 
  curl -s -o /dev/null -w "HTTP: %{http_code} (%{time_total}s)\n" http://$ip || echo "Falhou"
done
```
