data "azurerm_client_config" "me" {}

resource "random_string" "sfx" {
  length  = 5
  upper   = false
  special = false
}
resource "random_password" "pg" {
  length  = 24
  special = false
}
resource "random_password" "salt" {
  length  = 32
  special = false
}

locals {
  sfx  = random_string.sfx.result
  tags = { project = var.project, env = var.env }
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.project}-${var.env}"
  location = var.location
  tags     = local.tags
}

resource "azurerm_storage_account" "lake" {
  name                     = "st${var.project}${var.env}${local.sfx}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true
  min_tls_version          = "TLS1_2"
  tags                     = local.tags
}

resource "azurerm_storage_data_lake_gen2_filesystem" "layer" {
  for_each           = toset(["bronze", "silver", "gold"])
  name               = each.key
  storage_account_id = azurerm_storage_account.lake.id
}

resource "azurerm_key_vault" "kv" {
  name                      = "kv-${var.project}-${var.env}-${local.sfx}"
  resource_group_name       = azurerm_resource_group.rg.name
  location                  = var.location
  tenant_id                 = data.azurerm_client_config.me.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = true
  tags                      = local.tags
}

resource "azurerm_role_assignment" "kv_admin_me" {
  scope                = azurerm_key_vault.kv.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = data.azurerm_client_config.me.object_id
  principal_type       = "User"
}

resource "azurerm_key_vault_secret" "pg_password" {
  name         = "pg-password"
  value        = random_password.pg.result
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.kv_admin_me]
}
resource "azurerm_key_vault_secret" "pii_salt" {
  name         = "pii-salt"
  value        = random_password.salt.result
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.kv_admin_me]
}
resource "azurerm_key_vault_secret" "storage_key" {
  name         = "storage-key"
  value        = azurerm_storage_account.lake.primary_access_key
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.kv_admin_me]
}
resource "azurerm_postgresql_flexible_server" "pg" {
  name                   = "psql-${var.project}-${var.env}-${local.sfx}"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = var.pg_location
  version                = "16"
  administrator_login    = "finbankadmin"
  administrator_password = random_password.pg.result
  sku_name               = var.pg_sku
  storage_mb             = 32768
  backup_retention_days  = 7
  tags                   = local.tags
  lifecycle {
    ignore_changes = [zone]
  }
}

resource "azurerm_postgresql_flexible_server_database" "src" {
  name      = "finbank_source"
  server_id = azurerm_postgresql_flexible_server.pg.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "azure_services" {
  name             = "allow-azure-services"
  server_id        = azurerm_postgresql_flexible_server.pg.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}
resource "azurerm_postgresql_flexible_server_firewall_rule" "my_ip" {
  name             = "allow-my-ip"
  server_id        = azurerm_postgresql_flexible_server.pg.id
  start_ip_address = var.my_ip
  end_ip_address   = var.my_ip
}
resource "azurerm_log_analytics_workspace" "law" {
  name                = "law-${var.project}-${var.env}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.tags
}

resource "azurerm_monitor_action_group" "ag" {
  name                = "ag-${var.project}-${var.env}"
  resource_group_name = azurerm_resource_group.rg.name
  short_name          = "finbankdata"
  email_receiver {
    name          = "equipo-datos"
    email_address = var.alert_email
  }
}

resource "azurerm_monitor_diagnostic_setting" "lake_audit" {
  name                       = "auditoria-datalake"
  target_resource_id         = "${azurerm_storage_account.lake.id}/blobServices/default"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
  enabled_log {
    category = "StorageRead"
  }
  enabled_log {
    category = "StorageWrite"
  }
  enabled_log {
    category = "StorageDelete"
  }
}
resource "azurerm_databricks_workspace" "dbw" {
  name                = "dbw-${var.project}-${var.env}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  sku                 = "premium"
  tags                = local.tags
}



resource "azurerm_role_assignment" "engineers" {
  scope                = azurerm_storage_account.lake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = var.engineers_group_id
  principal_type       = "Group"
}
resource "azurerm_role_assignment" "analysts_gold" {
  scope                = "${azurerm_storage_account.lake.id}/blobServices/default/containers/gold"
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = var.analysts_group_id
  principal_type       = "Group"
  depends_on           = [azurerm_storage_data_lake_gen2_filesystem.layer]
}
resource "azurerm_role_assignment" "admins" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "Owner"
  principal_id         = var.admins_group_id
  principal_type       = "Group"
}