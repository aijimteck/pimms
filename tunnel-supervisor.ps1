$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$instanceDir = Join-Path $projectRoot "instance"
$publicUrlFile = Join-Path $instanceDir "public-url.txt"
$outLog = Join-Path $projectRoot "localhostrun.out.log"
$errLog = Join-Path $projectRoot "localhostrun.err.log"
$sshPath = "C:\WINDOWS\System32\OpenSSH\ssh.exe"
$sshArgs = @(
  "-o", "StrictHostKeyChecking=no",
  "-o", "ServerAliveInterval=60",
  "-R", "80:127.0.0.1:8000",
  "nokey@localhost.run"
)

Set-Location $projectRoot

if (-not (Test-Path $instanceDir)) {
  New-Item -ItemType Directory -Path $instanceDir | Out-Null
}

while ($true) {
  if (Test-Path $outLog) { Remove-Item $outLog -Force }
  if (Test-Path $errLog) { Remove-Item $errLog -Force }
  if (Test-Path $publicUrlFile) { Remove-Item $publicUrlFile -Force }

  $sshProcess = Start-Process `
    -FilePath $sshPath `
    -ArgumentList $sshArgs `
    -WorkingDirectory $projectRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput $outLog `
    -RedirectStandardError $errLog `
    -PassThru

  for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    if ($sshProcess.HasExited) {
      break
    }

    if (Test-Path $outLog) {
      $match = Select-String -Path $outLog -Pattern "https://[-a-z0-9]+\.lhr\.life" | Select-Object -First 1
      if ($match) {
        $publicUrl = $match.Matches[0].Value
        Set-Content -Path $publicUrlFile -Value $publicUrl -Encoding UTF8
        break
      }
    }
  }

  try {
    Wait-Process -Id $sshProcess.Id
  } catch {
  }

  Start-Sleep -Seconds 3
}
