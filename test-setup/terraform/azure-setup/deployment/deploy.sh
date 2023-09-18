#! /usr/bin/env bash

cd "C:\Users\janni\OneDrive\Dokumente\Projects\Python\simulation-framework\enosimulator\test-setup\terraform\azure-setup\deployment"

vulnbox_ip="108.142.137.233"

scp -i ../data/test_key ../data/test_key groot@${vulnbox_ip}:/home/groot/.ssh/test_key
scp -i ../data/test_key ./services.sh groot@${vulnbox_ip}:/home/groot/services.sh
scp -i ../data/test_key ./services.txt groot@${vulnbox_ip}:/home/groot/services.txt

checker_ip="108.142.137.253"

scp -i ../data/test_key ../data/test_key groot@${checker_ip}:/home/groot/.ssh/test_key
scp -i ../data/test_key ./checkers.sh groot@${checker_ip}:/home/groot/checkers.sh
scp -i ../data/test_key ./services.txt groot@${checker_ip}:/home/groot/services.txt

engine_ip="108.142.138.9"

scp -i ../data/test_key ../data/test_key groot@${engine_ip}:/home/groot/.ssh/test_key
scp -i ../data/test_key ./engine.sh groot@${engine_ip}:/home/groot/engine.sh