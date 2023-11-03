terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.72.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = _placeholder_
  client_id       = _placeholder_
  client_secret   = _placeholder_
  tenant_id       = _placeholder_
}
