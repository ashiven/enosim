#! /usr/bin/env bash

set -euo pipefail

setup_path=_placeholder_
ssh_config=_placeholder_
ssh_private_key_path=_placeholder_

cd ${setup_path}

if [ -n "${1-}" ] && [ "$1" == "-d" ]; then
    echo "[-] Destroying infrastructure ..."
    terraform destroy -auto-approve
    exit 0
fi

echo "[+] Building infrastructure ..."
terraform init
terraform validate
terraform apply -auto-approve
terraform output | tee ./logs/ip_addresses.log

checker_ip=$(grep -oP "checker_ip\s*=\s*\K[^\s]+" ./logs/ip_addresses.log)
engine_ip=$(grep -oP "engine_ip\s*=\s*\K[^\s]+" ./logs/ip_addresses.log)

echo "[+] Writing ssh config ..."
rm -f ${ssh_config}
echo -e "Host checker\nUser groot\nHostName ${checker_ip}\nIdentityFile ${ssh_private_key_path}\nStrictHostKeyChecking no\n" >>${ssh_config}
echo -e "Host engine\nUser groot\nHostName ${engine_ip}\nIdentityFile ${ssh_private_key_path}\nStrictHostKeyChecking no\n" >>${ssh_config}
