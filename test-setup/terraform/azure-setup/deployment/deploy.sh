#! /usr/bin/env bash

vulnbox_ip="52.148.209.211"
checker_ip="52.148.209.207"
engine_ip="40.119.129.17"
setup_path="C://Users//janni//OneDrive//Dokumente//Projects//Python//simulation-framework//enosimulator//test-setup//terraform//azure-setup"
ssh_config="C://Users//janni//.ssh//config"

cd "${setup_path}\deployment"
echo -e "Host vulnbox\nUser groot\nHostName ${vulnbox_ip}\nIdentityFile ${setup_path}//data//test_key\nStrictHostKeyChecking no\n
Host checker\nUser groot\nHostName ${checker_ip}\nIdentityFile ${setup_path}//data//test_key\nStrictHostKeyChecking no\n
Host engine\nUser groot\nHostName ${engine_ip}\nIdentityFile ${setup_path}//data//test_key\nStrictHostKeyChecking no" > ${ssh_config}

scp ../data/test_key vulnbox:/home/groot/.ssh/test_key
scp ./vulnbox.sh vulnbox:/home/groot/vulnbox.sh
scp ./services.txt vulnbox:/home/groot/services.txt


scp ../data/test_key checker:/home/groot/.ssh/test_key
scp ./checker.sh checker:/home/groot/checker.sh
scp ./services.txt checker:/home/groot/services.txt


scp ../data/test_key engine:/home/groot/.ssh/test_key
scp ./engine.sh engine:/home/groot/engine.sh