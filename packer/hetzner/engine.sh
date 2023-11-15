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

pat="<insert-your-pat-here>"

sudo git clone "https://${pat}@github.com/enowars/EnoEngine.git"
sudo git clone "https://${pat}@github.com/enowars/EnoCTFPortal.git"
sudo mkdir data

cd EnoEngine
sudo dotnet build
sudo docker compose up -d

cd ../EnoCTFPortal
echo "version: '3'

services:
  enolandingpage:
    restart: unless-stopped
    build: .
    environment:
      - \"ASPNETCORE_ENVIRONMENT=Development\"
      - \"EnoLandingPage__Title=SimulationCTF\"
      - \"EnoLandingPage__StartTime=2023-10-05T15:00:00Z\"
      - \"EnoLandingPage__RegistrationCloseOffset=48\"
      - \"EnoLandingPage__CheckInBeginOffset=12\"
      - \"EnoLandingPage__CheckInEndOffset=2\"
      - \"EnoLandingPage__HetznerVulnboxType=cx11\"
      - \"EnoLandingPage__HetznerCloudApiToken=...\"
      - \"EnoLandingPage__HetznerVulnboxImage=...\"
      - \"EnoLandingPage__HetznerVulnboxPubkey=...\"
      - \"EnoLandingPage__HetznerVulnboxLocation=...\"
      - \"EnoLandingPage__OAuthClientId=...\"
      - \"EnoLandingPage__OAuthClientSecret=...\"
      - \"EnoLandingPage__AdminSecret=...\"
    ports:
      - \"5001:80\"
    volumes:
      - ./sessions:/root/.aspnet/DataProtection-Keys
      - ./data:/app/data
      - ../data:/app/wwwroot/scoreboard" >docker-compose.yml
sudo docker compose up -d
