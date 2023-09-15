#!/bin/bash

services="services.txt"

if [ ! -f "$services" ]; then
    echo "Error: The file $services does not exist."
    exit 1
fi

echo "Starting to pull repositories..."

while read -r service_url; do
    service_name=$(basename "$service_url" .git) 
    service_name=$(echo $service_name | rev | cut -c6- | rev)

    if [ ! -d "$service_name" ]; then
        echo "Cloning $service_name..."
        git clone "$service_url"
    else
        echo "Pulling updates for $service_name..."
        cd "$service_name" || exit 1
        git pull
        cd ..
    fi
done < "$services"

echo "Finished pulling repositories."
