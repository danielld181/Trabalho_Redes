# Relatório do Processo de Desenvolvimento
## Dashboard de Análise de Tráfego de Servidor em Tempo Real

---

## 1. Visão Geral do Projeto

O projeto consistiu no desenvolvimento de um sistema de monitoramento de tráfego de rede em tempo real, com o objetivo de capturar, processar e visualizar dados de comunicação entre um servidor-alvo e diversos clientes. O sistema deveria exibir métricas em janelas de 5 segundos, permitindo análise detalhada do volume de tráfego por IP cliente e protocolo.

### Objetivos Principais
- Implementar captura de pacotes de rede focada em um servidor específico
- Desenvolver agregação de dados em janelas temporais discretas
- Construir interface interativa com drill-down por protocolo
- Implementar visualizações de dados complexas

---

## 2. Evolução do Desenvolvimento

### 2.1 Fase Inicial - Estruturação do Projeto
O projeto foi iniciado com a criação da estrutura básica de arquivos:
- **config.py**: Arquivo de configurações (vazio inicialmente)
- **main.py**: Ponto de entrada principal (vazio inicialmente)
- **__init__.py**: Arquivos de inicialização de pacotes
- **docs.txt**: Documentação técnica (vazio)

### 2.2 Configuração do Ambiente de Desenvolvimento

#### Shell NixOS (shell.nix)
Foi configurado um ambiente NixOS com todas as dependências necessárias:
```nix
buildInputs = with pkgs; [
  python3
  python3Packages.pandas
  python3Packages.openpyxl
  python3Packages.scapy
  python3Packages.requests
  nettools
  inetutils
  wireshark-cli
  tcpdump
  curl
  wget
  netcat
];
```

### 2.3 Desenvolvimento da Infraestrutura de Teste

#### VMs de Teste (ubuntu_vm_setup.sh)
Configuração automática de 5 VMs Ubuntu (192.168.122.10-14) com:
- **Servidor Apache**: Páginas web personalizadas por VM
- **Servidor FTP**: vsftpd configurado com acesso anônimo
- **SSH**: Serviço habilitado para conexões
- **Conteúdo customizado**: Páginas de teste e API mock

#### Gerador de Tráfego (generate_traffic.py)
Desenvolvido sistema sofisticado para gerar tráfego artificial:
- **Conexões persistentes**: HTTP Keep-Alive sessions
- **Múltiplos protocolos**: HTTP, TCP direto, ICMP
- **Tráfego contínuo**: Ciclos de 3 segundos com múltiplos endpoints
- **Threading**: Ping em background para manter atividade constante

---

## 3. Principais Desafios Enfrentados

### 3.1 Problema de Conectividade ICMP
**Sintoma**: Ping falhava consistentemente, mas HTTP funcionava
**Diagnóstico**:
- Criado script de diagnóstico detalhado (network_diagnostic.py)
- Script específico para debug ping vs HTTP (ping.py)
- Identificado que VMs não respondiam a ICMP ou firewall bloqueava

**Solução**:
- Modificação da lógica de detecção de "online" para usar HTTP ao invés de ping
- Implementação de fallback para múltiplos métodos de teste

### 3.2 Captura de Tráfego Real
**Desafio**: Sistema inicial não capturava tráfego real das VMs
**Análise**:
- Interface de rede incorreta sendo monitorada
- Necessidade de identificar interfaces bridge (virbr0, vnet1-5)
- Problemas com privilégios para captura de pacotes

**Solução**:
- Migração para análise de `/proc/net/dev` para métricas de interface
- Cálculo de deltas de tráfego entre medições
- Comando `ss` para análise de conexões ativas

### 3.3 Parsing e Formatação de Dados
**Problema**: Diferentes formatos de saída entre sistemas (vírgula vs ponto decimal)
**Solução**: Implementação de parsing robusto com replace(',', '.') para tempos de ping

---

## 4. Arquitetura Final Implementada

### 4.1 Monitor Principal (traffic_analyzer_excel.py)
**Funcionalidades Core**:
- **Coleta de Conexões**: Análise detalhada via comando `ss`
  - TCP estabelecidas, listening, UDP
  - Detalhes por protocolo e estado
- **Métricas de Interface**: Cálculo de deltas de tráfego
  - RX/TX bytes e packets por interface
  - Foco em interfaces VM (virbr0, vnet1-5)
- **Teste de Serviços**: Verificação multi-protocolo
  - HTTP com timing e status code
  - SSH/FTP via netcat
  - Ping com parsing melhorado

### 4.2 Estrutura de Dados
**Coleta por VM (janelas de 5s)**:
```python
data = {
    'timestamp': datetime,
    'vm_ip': str,
    'ping_time_ms': float,
    'ping_ok': bool,
    'tcp_established': int,
    'tcp_listening': int,
    'udp_connections': int,
    'total_connections': int,
    'http_status': int,
    'http_response_time_ms': float,
    'http_bytes_received': int,
    'ssh_service': bool,
    'ftp_service': bool,
    'interface_*_delta': int
}
```

### 4.3 Sistema de Relatórios Excel
**Múltiplas abas especializadas**:
- **Dados_Brutos**: Todos os dados coletados
- **Resumo_Detalhado**: Agregações por VM
- **Performance_VMs**: Análise estatística de latência
- **Timeline_Detalhada**: Últimas 100 medições
- **Estatisticas_Completas**: Métricas gerais do período

---

## 5. Scripts de Suporte Desenvolvidos

### 5.1 Diagnóstico de Rede (network_diagnostic.py)
Sistema completo de troubleshooting:
- Teste de serviços em todas as VMs
- Análise de conexões ativas
- Verificação de tráfego em interfaces
- Monitoramento em tempo real
- Análise de roteamento

### 5.2 Debug Específico (ping.py)
Diagnóstico focado no problema ICMP:
- Teste de ping com múltiplas opções
- Comparação ping vs HTTP
- Verificação de firewall
- Métodos alternativos (fping, hping3)

---

## 6. Resultados e Métricas Implementadas

### 6.1 Dados Coletados com Sucesso
- **Conectividade**: Status online/offline por VM
- **Latência**: Tempos de resposta HTTP e ping
- **Conexões**: Contagem detalhada por protocolo e estado
- **Throughput**: Deltas de bytes/packets por interface
- **Serviços**: Disponibilidade HTTP, SSH, FTP
- **Performance**: Estatísticas min/max/mean/std

### 6.2 Visualização em Excel
- Gráficos automáticos de timeline
- Tabelas pivô para análise por VM
- Métricas de disponibilidade e performance
- Relatórios de estatísticas completas

---

## 7. Lições Aprendidas

### 7.1 Desafios Técnicos
- **Ambiente NixOS**: Necessidade de configuração específica de capabilities
- **Virtualização**: Complexidade das interfaces de rede em ambientes VM
- **Privilégios**: Balanceamento entre segurança e funcionalidade
- **Parsing robusto**: Tratamento de diferentes formatos de saída

### 7.2 Evolução da Abordagem
- **Início**: Foco em captura de pacotes com Scapy
- **Evolução**: Migração para análise de métricas do sistema
- **Final**: Combinação de múltiplas fontes de dados

### 7.3 Debugging Sistemático
- Criação de scripts específicos para cada problema
- Logging detalhado para identificar causas-raiz
- Testes incrementais para validar soluções

---

## 8. Estado Final do Projeto

### 8.1 Funcionalidades Implementadas ✅
- ✅ Monitoramento em tempo real (janelas 5s)
- ✅ Coleta de métricas por VM cliente
- ✅ Análise de conexões por protocolo
- ✅ Geração de relatórios Excel detalhados
- ✅ Sistema de diagnóstico completo
- ✅ Infraestrutura de teste automatizada

### 8.2 Limitações Identificadas
- ❌ Dashboard web interativo não implementado
- ❌ API RESTful não desenvolvida
- ❌ Drill-down visual não implementado
- ⚠️ Dependência de ambiente NixOS específico

### 8.3 Dados Gerados
- **Arquivos Excel**: vm_traffic_analysis_*.xlsx com dados completos
- **Scripts funcionais**: Geração de tráfego e diagnóstico
- **Documentação**: Scripts comentados e auto-explicativos

---

## 9. Conclusão

O projeto evoluiu de uma proposta inicial de dashboard web para um sistema robusto de monitoramento e análise de rede em Excel. Embora não tenha atingido 100% dos objetivos originais (interface web e drill-down), desenvolveu-se um sistema funcional e bem documentado que:

1. **Coleta dados reais** de tráfego e conexões
2. **Processa informações** em janelas temporais
3. **Gera relatórios detalhados** para análise
4. **Inclui ferramentas de diagnóstico** completas
5. **Documenta o processo** de desenvolvimento

O processo de desenvolvimento demonstrou a importância de:
- **Debugging sistemático** para resolver problemas complexos
- **Flexibilidade de abordagem** quando soluções iniciais falham
- **Documentação contínua** do processo de resolução
- **Testes incrementais** para validar cada etapa

O sistema final, embora diferente da proposta original, representa uma solução completa e funcional para monitoramento de tráfego de rede em ambientes de laboratório.
