resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.azure_region

  tags = var.tags
}

module "network" {
  source = "./modules/network"

  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  project_name        = var.project_name
  environment         = var.environment
  tags                = var.tags
}

module "aks" {
  source = "./modules/aks"

  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  project_name        = var.project_name
  environment         = var.environment
  
  vnet_subnet_id = module.network.aks_subnet_id
  tags           = var.tags

  depends_on = [azurerm_resource_group.rg]
}

module "acr" {
  source = "./modules/acr"

  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  project_name        = var.project_name
  environment         = var.environment
  tags                = var.tags

  # Grant AKS managed identity permission to pull images
  aks_principal_id = module.aks.kubelet_identity_object_id

  depends_on = [azurerm_resource_group.rg]
}

module "keyvault" {
  source = "./modules/keyvault"

  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  project_name        = var.project_name
  environment         = var.environment
  tags                = var.tags

  # Grant AKS managed identity permission to read secrets
  aks_principal_id = module.aks.kubelet_identity_object_id

  depends_on = [azurerm_resource_group.rg]
}
