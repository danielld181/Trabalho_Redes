{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python e bibliotecas
    python3
    python3Packages.pandas
    python3Packages.openpyxl
    python3Packages.scapy
    python3Packages.requests
    python3Packages.pip

    # Shell e ferramentas básicas
    bash
    coreutils
    netcat
    # Ferramentas de rede
    nettools
    inetutils
    wireshark-cli
    tcpdump
    curl
    wget
    netcat
  ];

  shellHook = ''
    echo "🚀 Ambiente NixOS configurado para monitoramento de rede"
    echo "📊 Pacotes disponíveis: pandas, openpyxl, scapy"
    echo "🔧 Ferramentas: bash, curl, netcat, tcpdump"
    echo ""
    echo "▶️  Para gerar tráfego: bash generate_traffic.sh"
    echo "▶️  Para monitorar: sudo python3 traffic_analyzer_excel.py"
  '';
}
