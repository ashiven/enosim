#! /usr/bin/env bash

set -euo pipefail

echo "Installing necessary dependencies..."
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
# Add the repository to Apt sources:
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo apt-get install -y docker-compose-plugin
export DOCKER_BUILDKIT=0

pat=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
services="services.txt"
while read -r service_name; do
    echo "Cloning ${service_name}... "
    sudo git clone https://${pat}@github.com/enowars/enowars7-service-${service_name}.git

    sudo mv enowars7-service-${service_name}/service .
    sudo rm -rf enowars7-service-${service_name}
    sudo mv service ${service_name}
    cd ${service_name}

    echo "Starting ${service_name}..."
    sudo docker-compose up --build --force-recreate -d
    cd ..
done < "$services"

