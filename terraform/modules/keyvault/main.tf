data "azurerm_client_config" "current" {}

locals {
  keyvault_name = "kv-${var.project_name}-${var.environment}"
}

resource "azurerm_key_vault" "kv" {
  name                        = local.keyvault_name
  location                    = var.location
  resource_group_name         = var.resource_group_name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false
  enabled_for_deployment      = true
  enabled_for_disk_encryption = true
  enabled_for_template_deployment = true
  enable_rbac_authorization   = true

  tags = var.tags
}

# Grant AKS kubelet managed identity "Key Vault Secrets User" role
resource "azurerm_role_assignment" "aks_kv_secrets_user" {
  scope              = azurerm_key_vault.kv.id
  role_definition_name = "Key Vault Secrets User"
  principal_id       = var.aks_principal_id

  depends_on = [azurerm_key_vault.kv]
}

# Grant current user (who runs Terraform) full access to upload secrets
resource "azurerm_role_assignment" "current_user" {
  scope              = azurerm_key_vault.kv.id
  role_definition_name = "Key Vault Administrator"
  principal_id       = data.azurerm_client_config.current.object_id

  depends_on = [azurerm_key_vault.kv]
}

resource "azurerm_key_vault_secret" "acr_password" {
  count        = var.acr_admin_password != null ? 1 : 0
  name         = "acr-admin-password"
  value        = var.acr_admin_password
  key_vault_id = azurerm_key_vault.kv.id

  lifecycle {
    ignore_changes = [value]
  }
}

resource "azurerm_key_vault_secret" "sonar_token" {
  count        = var.sonar_token != null ? 1 : 0
  name         = "sonar-token"
  value        = var.sonar_token
  key_vault_id = azurerm_key_vault.kv.id

  lifecycle {
    ignore_changes = [value]
  }
}
