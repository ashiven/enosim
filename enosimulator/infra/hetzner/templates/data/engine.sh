#! /usr/bin/env bash

set -euo pipefail

sudo apt-get update
sudo apt-get install -y sysstat
sudo apt-get install -y ca-certificates curl gnupg
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

retry() {
  local retries=3
  until "$@" || [ "$retries" -eq 0 ]; do
    echo -e "\033[31m[!] Retrying command ...\033[0m"
    sleep 1
    retries=$((retries - 1))
  done
}

# Add the user to the docker group so we can execute docker commands remotely
sudo usermod -aG docker root

# If the image was built with packer move ctf.json to packer and cd into packer
if [ -d "../packer" ] && [ -f "ctf.json" ]; then
  sudo mv ctf.json ../packer
fi
if [ -d "../packer" ]; then
  cd ../packer
fi

# Clone the EnoEngine and the EnoCTFPortal if they haven't been cloned already and create the data directory if it doesn't exist
optional EnoEngine sudo git clone "https://${pat}@github.com/enowars/EnoEngine.git"
optional EnoCTFPortal sudo git clone "https://${pat}@github.com/enowars/EnoCTFPortal.git" && cd EnoCTFPortal && git reset --hard 7515883b && cd ..
optional data sudo mkdir data

# Move the ctf.json and docker-compose.yml to the EnoEngine and EnoCTFPortal directories if they haven't been moved already
if [ -f "./ctf.json" ]; then
  sudo mv ctf.json ./EnoEngine
fi
if [ -f "./docker-compose.yml" ]; then
  sudo mv docker-compose.yml ./EnoCTFPortal
fi

# Start the engine
echo -e "\033[32m[+] Starting EnoEngine ...\033[0m"
cd EnoEngine
retry sudo dotnet build
retry sudo docker compose up -d
retry sudo dotnet run --project EnoConfig apply
retry nohup sudo dotnet run -c Release --project EnoLauncher &>/dev/null &
retry nohup sudo dotnet run -c Release --project EnoFlagSink &>/dev/null &
sleep 5
retry nohup sudo dotnet run -c Release --project EnoEngine &>/dev/null &

# Wait for the engine to start before starting the scoreboard
sleep 10
cd ../EnoCTFPortal
retry sudo docker compose up -d

# Prune docker system if disk usage is above 90%
THRESHOLD=90
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
if [ "$DISK_USAGE" -gt "$THRESHOLD" ]; then
  docker system prune -a -f
fi
