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

#echo "Configuring vulnbox ..."
#scp ../data/test_key vulnbox:/home/groot/.ssh/test_key
#scp ./files/vulnbox.sh vulnbox:/home/groot/vulnbox.sh
#scp ./files/services.txt vulnbox:/home/groot/services.txt
#ssh vulnbox "chmod +x vulnbox.sh && ./vulnbox.sh"
#
#echo "Configuring checker ..."
#scp ../data/test_key checker:/home/groot/.ssh/test_key
#scp ./files/checker.sh checker:/home/groot/checker.sh
#scp ./files/services.txt checker:/home/groot/services.txt
#ssh checker "chmod +x checker.sh && ./checker.sh"

echo "Configuring engine ..."
scp ../data/test_key engine:/home/groot/.ssh/test_key
scp ./files/engine.sh engine:/home/groot/engine.sh
scp ./files/ctf.json engine:/home/groot/ctf.json
# ssh engine "mkdir data && chmod +x engine.sh && ./engine.sh"