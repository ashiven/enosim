#! /usr/bin/env bash

set -euo pipefail

echo -e "\033[32m[+] Installing necessary dependencies..."
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" |
  sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

sudo wget https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo rm packages-microsoft-prod.deb

sudo apt-get update
sudo apt-get install -y docker.io
sudo apt-get install -y dotnet-sdk-6.0
sudo systemctl start docker
sudo systemctl enable docker
sudo apt-get install -y docker-compose-plugin
sudo apt-get install -y pass gnupg2
export DOCKER_BUILDKIT=0

pat=_placeholder_

optional() {
  directory="$1"
  if [ ! -d "$directory" ]; then
    "${@:2}"
  fi
}

if [ -d "../packer" ] && [ -f "ctf.json" ]; then
  sudo mv ctf.json ../packer
fi

if [ -d "../packer" ]; then
  cd ../packer
fi

optional EnoEngine sudo git clone "https://${pat}@github.com/enowars/EnoEngine.git"
if [ -f "./ctf.json" ]; then
  sudo mv ctf.json ./EnoEngine
fi
optional data sudo mkdir data
cd EnoEngine

echo -e "\033[32m[+] Starting EnoEngine...\033[0m"
sudo docker compose up -d
sudo dotnet run --project EnoConfig apply
sudo dotnet run -c Release --project EnoLauncher &
sudo dotnet run -c Release --project EnoFlagSink &
sudo dotnet run -c Release --project EnoEngine &
