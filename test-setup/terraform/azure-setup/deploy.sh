#! /usr/bin/env bash

vulnbox_ip="52.148.209.211"
checker_ip="52.148.209.207"
engine_ip="40.119.129.17"
setup_path="C://Users//janni//OneDrive//Dokumente//Projects//Python//simulation-framework//enosimulator//test-setup//terraform//azure-setup"
ssh_config="C://Users//janni//.ssh//config"

cd ${setup_path}
echo -e "Host vulnbox\nUser groot\nHostName ${vulnbox_ip}\nIdentityFile ${setup_path}//data//id_rsa\nStrictHostKeyChecking no\n
Host checker\nUser groot\nHostName ${checker_ip}\nIdentityFile ${setup_path}//data//id_rsa\nStrictHostKeyChecking no\n
Host engine\nUser groot\nHostName ${engine_ip}\nIdentityFile ${setup_path}//data//id_rsa\nStrictHostKeyChecking no" > ${ssh_config}

echo "Building infrastructure ..."
terraform init
terraform validate
terraform apply -auto-approve

echo "Configuring vulnbox ..."
scp ./data/id_rsa vulnbox:/home/groot/.ssh/id_rsa
scp ./data/vulnbox.sh vulnbox:/home/groot/vulnbox.sh
scp ./data/services.txt vulnbox:/home/groot/services.txt
ssh vulnbox "chmod +x vulnbox.sh && ./vulnbox.sh"

echo "Configuring checker ..."
scp ./data/id_rsa checker:/home/groot/.ssh/id_rsa
scp ./data/checker.sh checker:/home/groot/checker.sh
scp ./data/services.txt checker:/home/groot/services.txt
ssh checker "chmod +x checker.sh && ./checker.sh"

echo "Configuring engine ..."
scp ../data/id_rsa engine:/home/groot/.ssh/id_rsa
scp ./data/engine.sh engine:/home/groot/engine.sh
scp ./data/ctf.json engine:/home/groot/ctf.json
ssh engine "mkdir data && chmod +x engine.sh && ./engine.sh"