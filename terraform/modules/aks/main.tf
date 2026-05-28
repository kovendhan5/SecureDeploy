locals {
  cluster_name = "aks-${var.project_name}-${var.environment}"
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = local.cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "${var.project_name}${var.environment}"
  kubernetes_version  = "1.28"

  # Default node pool configuration
  default_node_pool {
    name                         = "system"
    node_count                   = 2
    vm_size                      = "Standard_B2s" # Cheapest option for student tier
    zones                        = ["1"]
    vnet_subnet_id              = var.vnet_subnet_id
    only_critical_addons_enabled = true

    # Autoscaling
    enable_auto_scaling = true
    min_count           = 2
    max_count           = 4

    tags = var.tags
  }

  # System-assigned managed identity
  identity {
    type = "SystemAssigned"
  }

  # Kubelet identity for ACR pull
  kubelet_identity {
    client_id                 = azurerm_user_assigned_identity.kubelet.client_id
    object_id                 = azurerm_user_assigned_identity.kubelet.principal_id
    user_assigned_identity_id = azurerm_user_assigned_identity.kubelet.id
  }

  network_profile {
    network_plugin = "azure"
    network_policy = "azure"
  }

  http_application_routing_enabled = false
  role_based_access_control_enabled = true

  tags = var.tags

  depends_on = [
    azurerm_user_assigned_identity.kubelet
  ]
}

# Managed identity for kubelet to pull from ACR and access Key Vault
resource "azurerm_user_assigned_identity" "kubelet" {
  resource_group_name = var.resource_group_name
  location            = var.location
  name                = "mi-kubelet-${var.project_name}-${var.environment}"

  tags = var.tags
}
