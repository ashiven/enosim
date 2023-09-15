#!/bin/bash

echo "Starting local Kubernetes cluster with Minikube"
minikube start

services="services.txt"

if [ ! -f "$services" ]; then
    echo "Error: The file $services does not exist."
    exit 1
fi

echo "Deploying services to Kubernetes cluster..."

while read -r service_url; do
    service_name=$(basename "$service_url" .git) 
    service_name=$(echo $service_name | rev | cut -c6- | rev)

    if [ ! -d "$service_name" ]; then
        echo "Could not find $service_name in the current directory"
    else
        cd "$service_name" || exit 1
        echo "Deploying checker for $service_name"
        kubectl apply -f kube-checker
        echo "Deploying service for $service_name"
        kubectl apply -f kube-service
        cd ..
    fi
done < "$services"

echo "Finished pulling repositories."