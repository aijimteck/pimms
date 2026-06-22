$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$publicUrlFile = Join-Path $projectRoot "instance\public-url.txt"

$appProcess = Get-CimInstance Win32_Process |
  Where-Object { $_.Name -eq "python.exe" -and $_.CommandLine -match "app.py" } |
  Select-Object -First 1

$supervisorProcess = Get-CimInstance Win32_Process |
  Where-Object { $_.Name -eq "powershell.exe" -and $_.CommandLine -match "tunnel-supervisor\.ps1" } |
  Select-Object -First 1

$publicUrl = ""
if (Test-Path $publicUrlFile) {
  $publicUrl = (Get-Content $publicUrlFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
}

Write-Host "Serveur local : http://127.0.0.1:8000"
Write-Host "Serveur actif : $([bool]$appProcess)"
Write-Host "Superviseur tunnel actif : $([bool]$supervisorProcess)"

if ($publicUrl) {
  Write-Host "URL publique : $publicUrl"
  Write-Host "Administration : $publicUrl/?mode=tableau"
} else {
  Write-Host "URL publique : non disponible pour le moment"
}
