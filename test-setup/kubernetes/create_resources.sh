#!/bin/bash

services="services.txt"
kompose() {
    # change this command for different kinds of deployments 
    kompose convert
}

if [ ! -f "$services" ]; then
    echo "Error: The file $services does not exist."
    exit 1
fi

echo "Creating Kubernetes resources for services"

while read -r service_url; do
    service_name=$(basename "$service_url" .git) 
    service_name=$(echo $service_name | rev | cut -c6- | rev)

    if [ ! -d "$service_name" ]; then
        echo "Could not find $service_name in the current directory"
    else
        echo "Creating resources for $service_name..."
        cd "$service_name" || exit 1
        mkdir kube-checker
        mkdir kube-service
        cd checker
        kompose
        for yaml_file in *.yaml; do
            if [ "$yaml_file" != "docker-compose.yaml" ]; then
                mv "$yaml_file" ../kube-checker/
            fi
        done
        echo "Created checker resource files"
        cd ../service
        kompose
        for yaml_file in *.yaml; do
            if [ "$yaml_file" != "docker-compose.yaml" ]; then
                mv "$yaml_file" ../kube-service/
            fi
        done
        echo "Created service resource files"
        cd ../..
    fi
done < "$services"

echo "Finished creating resources."