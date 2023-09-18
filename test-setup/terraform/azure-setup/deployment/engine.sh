#! /usr/bin/env bash

set -euo pipefail

pat=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

echo "Installing necessary dependencies..."
sudo wget https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo rm packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y docker.io
sudo apt-get install -y dotnet-sdk-7.0
sudo systemctl start docker
sudo systemctl enable docker
sudo apt-get install -y docker-compose
export DOCKER_BUILDKIT=0

echo "Starting EnoEngine..."
sudo git clone "https://${pat}@github.com:enowars/EnoEngine.git"
cd EnoEngine
sudo docker-compose up -d
sudo dotnet run --project EnoConfig apply
sudo dotnet run -c Release --project EnoLauncher
sudo dotnet run -c Release --project EnoFlagSink
sudo dotnet run -c Release --project EnoEngine