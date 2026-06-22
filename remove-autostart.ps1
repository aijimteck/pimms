$ErrorActionPreference = "Stop"

$taskName = "PIMMS-Accueil-Autostart"

if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
  Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
  Write-Host "Tâche planifiée supprimée : $taskName"
} else {
  Write-Host "Aucune tâche planifiée à supprimer."
}
