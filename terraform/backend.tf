terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.70"
    }
  }

  # Uncomment and configure after creating the storage account manually
  # Or follow the instructions below to create it first
  # backend "azurerm" {
  #   resource_group_name  = "rg-securedeploy-tfstate"
  #   storage_account_name = "stsecuredeploytf"
  #   container_name       = "tfstate"
  #   key                  = "securedeploy.terraform.tfstate"
  # }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
      recover_soft_deleted_keys    = true
    }
  }
}

# Initial setup: Create storage account for Terraform state
# Run this first, then enable the backend block above
# az group create --name rg-securedeploy-tfstate --location "East US"
# az storage account create --resource-group rg-securedeploy-tfstate --name stsecuredeploytf --sku Standard_LRS --encryption-services blob
# az storage container create --name tfstate --account-name stsecuredeploytf --auth-mode login
