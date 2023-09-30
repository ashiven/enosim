#! /usr/bin/env bash

set -euo pipefail

setup_path=_placeholder_
ssh_config=_placeholder_
ssh_private_key_path=_placeholder_

cd ${setup_path}

if [ -n "${1-}" ] && [ "$1" == "-d" ]; then
    echo -e "\033[31m[-] Destroying infrastructure ...\033[0m"
    terraform destroy -auto-approve
    exit 0
fi

echo -e "\033[32m[+] Building infrastructure ...\033[0m"
terraform init
terraform validate
terraform apply -auto-approve
terraform output >./logs/ip_addresses.log

checker_ip=$(grep -oP "checker\s*=\s*\K[^\s]+" ./logs/ip_addresses.log | sed 's/"//g')
engine_private_ip=$(grep -oP "\s*\"engine\"\s*=\s*\K[^\s]+" ./logs/ip_addresses.log | sed 's/"//g')
engine_ip=$(grep -oP "engine\s*=\s*\K[^\s]+" ./logs/ip_addresses.log | sed 's/"//g')

rm -f ${ssh_config}
echo -e "\n\033[32m[+] Writing ssh config ...\033[0m"
echo -e "Host checker\nUser groot\nHostName ${checker_ip}\nIdentityFile ${ssh_private_key_path}\nStrictHostKeyChecking no\n" >>${ssh_config}
echo -e "Host engine\nUser groot\nHostName ${engine_ip}\nIdentityFile ${ssh_private_key_path}\nStrictHostKeyChecking no\n" >>${ssh_config}
