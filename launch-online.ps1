$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$instanceDir = Join-Path $projectRoot "instance"
$publicUrlFile = Join-Path $instanceDir "public-url.txt"
$outLog = Join-Path $projectRoot "localhostrun.out.log"
$errLog = Join-Path $projectRoot "localhostrun.err.log"
$supervisorScript = Join-Path $projectRoot "tunnel-supervisor.ps1"

Set-Location $projectRoot

if (-not (Test-Path $instanceDir)) {
  New-Item -ItemType Directory -Path $instanceDir | Out-Null
}

Write-Host "Installation des dépendances Python..."
python -m pip install -r requirements.txt | Out-Null

$existingApp = Get-CimInstance Win32_Process |
  Where-Object { $_.Name -eq "python.exe" -and $_.CommandLine -match "app.py" } |
  Select-Object -First 1

if (-not $existingApp) {
  Write-Host "Démarrage du serveur..."
  $server = Start-Process `
    -FilePath "python" `
    -ArgumentList "app.py" `
    -WorkingDirectory $projectRoot `
    -WindowStyle Hidden `
    -PassThru
} else {
  $server = $null
  Write-Host "Serveur déjà actif sur cette machine."
}

$existingSupervisor = Get-CimInstance Win32_Process |
  Where-Object { $_.Name -eq "powershell.exe" -and $_.CommandLine -match "tunnel-supervisor\.ps1" }

foreach ($process in $existingSupervisor) {
  Stop-Process -Id $process.ProcessId -Force
}

if (Test-Path $outLog) { Remove-Item $outLog -Force }
if (Test-Path $errLog) { Remove-Item $errLog -Force }
if (Test-Path $publicUrlFile) { Remove-Item $publicUrlFile -Force }

Write-Host "Démarrage du superviseur de tunnel..."
$supervisor = Start-Process `
  -FilePath "powershell.exe" `
  -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-File", $supervisorScript `
  -WorkingDirectory $projectRoot `
  -WindowStyle Hidden `
  -PassThru

$publicUrl = ""
for ($i = 0; $i -lt 24; $i++) {
  Start-Sleep -Milliseconds 500
  if (Test-Path $publicUrlFile) {
    $publicUrl = (Get-Content $publicUrlFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
    if ($publicUrl) {
      break
    }
  }
}

Write-Host ""
Write-Host "Serveur local : http://127.0.0.1:8000"
if ($publicUrl) {
  Write-Host "URL publique : $publicUrl"
} else {
  Write-Host "URL publique : en attente. Consultez $publicUrlFile ou localhostrun.out.log."
}
if ($server) {
  Write-Host "PID serveur : $($server.Id)"
}
Write-Host "PID superviseur : $($supervisor.Id)"
