#! /usr/bin/env bash

set -euo pipefail

setup_path=_placeholder_
ssh_config=_placeholder_

cd ${setup_path}

retry() {
  local retries=3
  until "$@" || [ "$retries" -eq 0 ]; do
    echo "[!] Retrying command ..."
    sleep 1
    retries=$((retries - 1))
  done
}

echo "[+] Configuring checker ..."
retry scp -F ${ssh_config} ./data/checker.sh checker:/home/groot/checker.sh
retry scp -F ${ssh_config} ./config/services.txt checker:/home/groot/services.txt
echo "[!] This will take a few minutes. Please be patient."
retry ssh -F ${ssh_config} checker "chmod +x checker.sh && ./checker.sh" >./logs/checker_config.log 2>&1

echo "[+] Configuring engine ..."
retry scp -F ${ssh_config} ./data/engine.sh engine:/home/groot/engine.sh
retry scp -F ${ssh_config} ./config/ctf.json engine:/home/groot/ctf.json
echo "[!] This will take a few minutes. Please be patient."
retry ssh -F ${ssh_config} engine "mkdir data && chmod +x engine.sh && ./engine.sh" >./logs/engine_config.log 2>&1
