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

sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo apt-get install -y docker-compose-plugin
export DOCKER_BUILDKIT=0

retry() {
  local retries=3
  until "$@" || [ "$retries" -eq 0 ]; do
    echo -e "\033[31m[!] Retrying command ...\033[0m"
    sleep 1
    retries=$((retries - 1))
  done
}

pat="<insert-your-pat-here>"

services=(
  "enowars7-service-CVExchange"
  "enowars7-service-bollwerk"
  "enowars7-service-yvm"
  "enowars7-service-asocialnetwork"
  "enowars7-service-oldschool"
  "enowars7-service-granulizer"
  "enowars7-service-phreaking"
)

for service in "${services[@]}"; do
  sudo git clone "https://${pat}@github.com/enowars/${service}.git"
  sudo find "${service}" \( -name "requirements*" -o -name "Dockerfile*" \) -exec sed -i "s|enochecker3[^ ]*|git+https://github.com/ashiven/enochecker3|g" "{}" \;

  cd "${service}/service"
  retry sudo docker compose up --build --force-recreate -d

  cd "../checker"
  retry sudo docker compose up --build --force-recreate -d
  cd ../../
done
