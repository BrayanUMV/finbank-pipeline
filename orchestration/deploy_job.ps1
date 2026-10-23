# Crea o actualiza el job diario en Databricks a partir de la plantilla.
# Toma el usuario y el tamaño de máquina del clúster que ya funciona. No contiene secretos.
$ErrorActionPreference = "Stop"

$nombre = "finbank-pipeline-diario"
$ME = (databricks current-user me | ConvertFrom-Json).userName
$cl = databricks clusters list -o json | ConvertFrom-Json | Select-Object -First 1
if (-not $cl) { throw "No hay ningún clúster de referencia. Crea uno en Compute primero." }

Write-Host "Usuario:        $ME"
Write-Host "Runtime:        $($cl.spark_version)"
Write-Host "Tipo de nodo:   $($cl.node_type_id)"

$plantilla = Get-Content "orchestration\finbank_job.template.json" -Raw -Encoding UTF8
$json = $plantilla.Replace("__USER__", $ME).Replace("__EMAIL__", $ME).Replace("__SPARK_VERSION__", $cl.spark_version).Replace("__NODE_TYPE__", $cl.node_type_id)

$utf8 = New-Object System.Text.UTF8Encoding($false)    # UTF-8 sin BOM, para que el CLI lo lea bien
$tmp = Join-Path $env:TEMP "finbank_job.json"

$existe = databricks jobs list -o json | ConvertFrom-Json | Where-Object { $_.settings.name -eq $nombre } | Select-Object -First 1

if ($existe) {
    $payload = @{ job_id = $existe.job_id; new_settings = ($json | ConvertFrom-Json) } | ConvertTo-Json -Depth 20
    [System.IO.File]::WriteAllText($tmp, $payload, $utf8)
    databricks jobs reset --json "@$tmp"
    Write-Host "Job actualizado. job_id = $($existe.job_id)"
} else {
    [System.IO.File]::WriteAllText($tmp, $json, $utf8)
    databricks jobs create --json "@$tmp"
}
