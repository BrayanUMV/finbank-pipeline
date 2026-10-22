output "resource_group" {
  value = azurerm_resource_group.rg.name
}
output "storage_account_name" {
  value = azurerm_storage_account.lake.name
}
output "key_vault_name" {
  value = azurerm_key_vault.kv.name
}
output "pg_host" {
  value = azurerm_postgresql_flexible_server.pg.fqdn
}
output "databricks_url" {
  value = "https://${azurerm_databricks_workspace.dbw.workspace_url}"
}
output "log_analytics_id" {
  value = azurerm_log_analytics_workspace.law.id
}
output "action_group_id" {
  value = azurerm_monitor_action_group.ag.id
}