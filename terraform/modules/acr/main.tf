locals {
  acr_name = replace("acr${var.project_name}${var.environment}", "-", "")  # ACR names must be alphanumeric
}

resource "azurerm_container_registry" "acr" {
  name                = local.acr_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Basic"  # Cheapest option for student tier
  admin_enabled       = true

  tags = var.tags
}

# Grant AKS kubelet managed identity AcrPull role on ACR
resource "azurerm_role_assignment" "aks_acr_pull" {
  scope              = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id       = var.aks_principal_id

  depends_on = [azurerm_container_registry.acr]
}
