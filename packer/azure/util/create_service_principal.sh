#! /usr/bin/env bash

set -euo pipefail

# Login to Azure
az login

# List the subscriptions for the account
az account list

# Set the subscription (if you have more than one subscription)
az account set --subscription "<subscription_id>"

# Create a service principal for the Azure subscription
az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/<subscription_id>"

# Login to Azure with the service principal
az login --service-principal -u "<client_id>" -p "<client_secret>" --tenant "<tenant_id>"

# Logout from Azure
az logout
