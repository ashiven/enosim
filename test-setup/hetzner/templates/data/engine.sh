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

# Expose docker daemon so we can get the stats of the containers
sudo mkdir -p /etc/systemd/system/docker.service.d
echo -e "[Service]\nExecStart=\nExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375" | sudo tee /etc/systemd/system/docker.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl restart docker.service

# If the image was built with packer move ctf.json to packer and cd into packer
if [ -d "../packer" ] && [ -f "ctf.json" ]; then
  sudo mv ctf.json ../packer
fi
if [ -d "../packer" ]; then
  cd ../packer
fi

# Clone the EnoEngine and the EnoCTFPortal if they haven't been cloned already and create the data directory if it doesn't exist
optional EnoEngine sudo git clone "https://${pat}@github.com/enowars/EnoEngine.git"
optional EnoCTFPortal sudo git clone "https://${pat}@github.com/enowars/EnoCTFPortal.git"
optional data sudo mkdir data

# Move the ctf.json and docker-compose.yml to the EnoEngine and EnoCTFPortal directories if they haven't been moved already
if [ -f "./ctf.json" ]; then
  sudo mv ctf.json ./EnoEngine
fi
if [ -f "./docker-compose.yml" ]; then
  sudo mv docker-compose.yml ./EnoCTFPortal
fi

# Start the engine
echo -e "\033[32m[+] Starting EnoEngine...\033[0m"
cd EnoEngine
sudo dotnet build
sudo docker compose up -d
sudo dotnet run --project EnoConfig apply
sudo dotnet run -c Release --project EnoLauncher &
sudo dotnet run -c Release --project EnoFlagSink &
sleep 6
sudo dotnet run -c Release --project EnoEngine &

# Wait for the engine to start before starting the scoreboard
sleep 45
cd ../EnoCTFPortal
sudo docker compose up -d
exit 0
