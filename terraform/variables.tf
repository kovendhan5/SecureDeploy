variable "azure_region" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "securedeploy"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    project     = "securedeploy"
    environment = "prod"
    owner       = "DevOps"
    created_by  = "terraform"
  }
}
