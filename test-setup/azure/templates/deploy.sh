#! /usr/bin/env bash

set -euo pipefail

setup_path="C://Users//janni//OneDrive//Dokumente//Projects//Python//simulation-framework//enosimulator//test-setup//azure"
ssh_config="C://Users//janni//.ssh//simconfig"

cd ${setup_path}

retry() {
  until "$@"; do
    echo "[!] Retrying command ..."
    sleep 1
  done
}

echo "[+] Configuring vulnbox ..."
retry scp -F ${ssh_config} ./data/vulnbox.sh vulnbox:/home/groot/vulnbox.sh
retry scp -F ${ssh_config} ./config/services.txt vulnbox:/home/groot/services.txt
echo "[!] This will take a few minutes. Please be patient."
retry ssh -F ${ssh_config} vulnbox "chmod +x vulnbox.sh && ./vulnbox.sh" >./logs/vulnbox_config.log 2>&1

echo "[+] Configuring checker ..."
retry scp -F ${ssh_config} ./data/checker.sh checker:/home/groot/checker.sh
retry scp -F ${ssh_config} ./config/services.txt checker:/home/groot/services.txt
echo "[!] This will take a few minutes. Please be patient."
retry ssh -F ${ssh_config} checker "chmod +x checker.sh && ./checker.sh" >./logs/checker_config.log 2>&1

echo "[+] Configuring engine ..."
retry scp -F ${ssh_config} ./data/engine.sh engine:/home/groot/engine.sh
retry scp -F ${ssh_config} ./config/ctf.json engine:/home/groot/ctf.json
retry ssh -F ${ssh_config} engine "mkdir data && chmod +x engine.sh && ./engine.sh" >./logs/engine_config.log 2>&1 &
