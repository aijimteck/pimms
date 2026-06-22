$ErrorActionPreference = "Stop"

$targets = @(
  Get-CimInstance Win32_Process | Where-Object {
    ($_.Name -eq "python.exe" -and $_.CommandLine -match "app.py") -or
    ($_.Name -eq "powershell.exe" -and $_.CommandLine -match "tunnel-supervisor\.ps1") -or
    ($_.Name -eq "ssh.exe" -and $_.CommandLine -match "localhost.run")
  }
)

if (-not $targets) {
  Write-Host "Aucun processus du formulaire n'est en cours."
  exit 0
}

foreach ($process in $targets) {
  Stop-Process -Id $process.ProcessId -Force
}

Write-Host "Serveur et tunnel arrêtés."
