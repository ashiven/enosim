#! /usr/bin/env bash

set -euo pipefail

setup_path="C://Users//janni//OneDrive//Dokumente//Projects//Python//simulation-framework//enosimulator//test-setup//terraform//azure-setup"
ssh_config="C://Users//janni//.ssh//simconfig"
cd ${setup_path}

if [ -n "${1-}" ] && [ "$1" == "-d" ]; then
  echo "Destroying infrastructure ..."
  terraform destroy -auto-approve
  exit 0  
fi

echo "Building infrastructure ..."
terraform init
terraform validate
terraform apply -auto-approve
terraform output | tee output.txt

vulnbox_ip=$(grep -oP "vulnbox_ip = \K[^\s]+" ./output.txt)
checker_ip=$(grep -oP "checker_ip = \K[^\s]+" ./output.txt)
engine_ip=$(grep -oP "engine_ip = \K[^\s]+" ./output.txt)
rm output.txt

echo "Writing ssh config ..."
echo -e "Host vulnbox\nUser groot\nHostName ${vulnbox_ip}\nIdentityFile ${setup_path}//data//id_rsa\nStrictHostKeyChecking no\n
Host checker\nUser groot\nHostName ${checker_ip}\nIdentityFile ${setup_path}//data//id_rsa\nStrictHostKeyChecking no\n
Host engine\nUser groot\nHostName ${engine_ip}\nIdentityFile ${setup_path}//data//id_rsa\nStrictHostKeyChecking no" > ${ssh_config}

echo "Configuring vulnbox ..."
scp -F ${ssh_config} ./data/vulnbox.sh vulnbox:/home/groot/vulnbox.sh
scp -F ${ssh_config} ./config/services.txt vulnbox:/home/groot/services.txt
ssh -F ${ssh_config} vulnbox "chmod +x vulnbox.sh && ./vulnbox.sh" > ./logs/vulnbox_config.log &

echo "Configuring checker ..."
scp -F ${ssh_config} ./data/checker.sh checker:/home/groot/checker.sh
scp -F ${ssh_config} ./config/services.txt checker:/home/groot/services.txt
ssh -F ${ssh_config} checker "chmod +x checker.sh && ./checker.sh" > checker_config.log &

echo "Configuring engine ..."
scp -F ${ssh_config} ./data/engine.sh engine:/home/groot/engine.sh
scp -F ${ssh_config} ./config/ctf.json engine:/home/groot/ctf.json
ssh -F ${ssh_config} engine "mkdir data && chmod +x engine.sh && ./engine.sh" > engine_config.log &
