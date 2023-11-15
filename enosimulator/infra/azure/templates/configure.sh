#! /usr/bin/env bash

set -euo pipefail

setup_path=_placeholder_
ssh_config=_placeholder_

cd ${setup_path}

retry() {
  local retries=5
  until "$@" || [ "$retries" -eq 0 ]; do
    echo -e "\033[31m[!] Retrying command ...\033[0m"
    sleep 2
    retries=$((retries - 1))
  done
}

echo -e "\n\033[32m[+] Configuring checker ...\033[0m"
retry scp -F ${ssh_config} ./data/checker.sh checker:/home/groot/checker.sh
retry scp -F ${ssh_config} ./config/services.txt checker:/home/groot/services.txt
retry ssh -F ${ssh_config} checker "chmod +x checker.sh && ./checker.sh" >./logs/checker_config.log 2>&1 &

wait -n

echo -e "\n\033[32m[+] Configuring engine ...\033[0m"
retry scp -F ${ssh_config} ./data/engine.sh engine:/home/groot/engine.sh
retry scp -F ${ssh_config} ./data/docker-compose.yml engine:/home/groot/docker-compose.yml
retry scp -F ${ssh_config} ./config/ctf.json engine:/home/groot/ctf.json
retry ssh -F ${ssh_config} engine "chmod +x engine.sh && ./engine.sh" | tee ./logs/engine_config.log 2>&1
