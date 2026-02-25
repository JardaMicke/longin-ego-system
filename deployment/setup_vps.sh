#!/bin/bash
# setup_vps.sh
# Automatizovaný skript pro přípravu VPS serveru pro LONGIN EGO System
# Tento skript nainstaluje Docker a (volitelně) NVIDIA Container Toolkit

set -e # Zastaví skript při chybě

echo "=== LONGIN EGO VPS Setup ==="
echo "1. Aktualizace systému..."
sudo apt update && sudo apt upgrade -y

echo "2. Instalace prerekvizit..."
sudo apt install -y curl git apt-transport-https ca-certificates software-properties-common pciutils

echo "3. Instalace Dockeru..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Přidání aktuálního uživatele do skupiny docker
current_user=$(whoami)
sudo usermod -aG docker $current_user
echo "   Uživatel $current_user přidán do skupiny docker."

echo "4. Kontrola GPU..."
if lspci | grep -i nvidia > /dev/null; then
    echo "   NVIDIA GPU detekováno. Instaluji NVIDIA Container Toolkit..."
    
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    
    sudo apt update && sudo apt install -y nvidia-docker2
    sudo systemctl restart docker
    echo "   NVIDIA Container Toolkit nainstalován."
else
    echo "   Žádná NVIDIA GPU nedetekována (nebo lspci nenašlo 'nvidia'). Přeskakuji instalaci ovladačů."
fi

echo ""
echo "=== Hotovo! ==="
echo "Prosím odhlašte se a znovu přihlašte (nebo restartujte server), aby se projevily změny oprávnění pro Docker."
echo "Poté můžete pokračovat nahráním projektu."
