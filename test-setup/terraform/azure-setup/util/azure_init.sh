#!/bin/bash

# to use the german azure cloud
# az cloud set --name AzureGermanCloud

# the default cloud 
# az cloud set --name AzureCloud

# login to azure via cli
az login

# view subscriptions
# az account list

# optionally specify subscription if you have multiple subscriptions
# az account set --subscription="SUBSCRIPTION_ID"