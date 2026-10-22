# Configura Databricks: login y secret scope "finbank".
# No contiene secretos: los lee de Key Vault o los pide por pantalla.
$ErrorActionPreference = "Stop"

$ACCT = terraform -chdir=infra output -raw storage_account_name
$KV   = terraform -chdir=infra output -raw key_vault_name
$PGH  = terraform -chdir=infra output -raw pg_host
$DBX  = terraform -chdir=infra output -raw databricks_url

function Get-KvSecret($nombre) {
    az keyvault secret show --vault-name $KV --name $nombre --query value -o tsv
}

databricks auth login --host $DBX

# Si el scope ya existe, el error se ignora y se continúa
try { databricks secrets create-scope finbank } catch { Write-Host "El scope finbank ya existe." }

databricks secrets put-secret finbank storage-account --string-value $ACCT
databricks secrets put-secret finbank storage-key     --string-value (Get-KvSecret "storage-key")
databricks secrets put-secret finbank pg-host         --string-value $PGH
databricks secrets put-secret finbank pg-user         --string-value "finbankadmin"
databricks secrets put-secret finbank pg-password     --string-value (Get-KvSecret "pg-password")
databricks secrets put-secret finbank pii-salt        --string-value (Get-KvSecret "pii-salt")

$mail   = Read-Host "Correo que RECIBE las alertas"
$smtpU  = Read-Host "Gmail que ENVIA las alertas"
$smtpP  = Read-Host "Contraseña de aplicación (16 caracteres)" -AsSecureString
$smtpPl = [System.Net.NetworkCredential]::new("", $smtpP).Password

databricks secrets put-secret finbank alert-email --string-value $mail
databricks secrets put-secret finbank smtp-user   --string-value $smtpU
databricks secrets put-secret finbank smtp-pass   --string-value $smtpPl

Write-Host "Secretos guardados:"
databricks secrets list-secrets finbank