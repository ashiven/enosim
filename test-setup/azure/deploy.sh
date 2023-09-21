#! /usr/bin/env bash

set -euo pipefail

setup_path="C://Users//janni//OneDrive//Dokumente//Projects//Python//simulation-framework//enosimulator//test-setup//azure"
ssh_config="C://Users//janni//.ssh//simconfig"

cd ${setup_path}

ssh_cmd() {
  until "$@"; do
    echo "Retrying ssh connection..."
    sleep 1
  done
}

echo "Configuring vulnbox ..."
ssh_cmd scp -F ${ssh_config} ./data/vulnbox.sh vulnbox:/home/groot/vulnbox.sh
ssh_cmd scp -F ${ssh_config} ./config/services.txt vulnbox:/home/groot/services.txt
echo "This will take a few minutes. Please be patient."
ssh_cmd ssh -F ${ssh_config} vulnbox "chmod +x vulnbox.sh && ./vulnbox.sh" >./logs/vulnbox_config.log 2>&1

echo "Configuring checker ..."
ssh_cmd scp -F ${ssh_config} ./data/checker.sh checker:/home/groot/checker.sh
ssh_cmd scp -F ${ssh_config} ./config/services.txt checker:/home/groot/services.txt
echo "This will take a few minutes. Please be patient."
ssh_cmd ssh -F ${ssh_config} checker "chmod +x checker.sh && ./checker.sh" >./logs/checker_config.log 2>&1

echo "Configuring engine ..."
ssh_cmd scp -F ${ssh_config} ./data/engine.sh engine:/home/groot/engine.sh
ssh_cmd scp -F ${ssh_config} ./config/ctf.json engine:/home/groot/ctf.json
ssh_cmd ssh -F ${ssh_config} engine "mkdir data && chmod +x engine.sh && ./engine.sh" >./logs/engine_config.log 2>&1 &
