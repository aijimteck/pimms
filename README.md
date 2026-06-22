# Formulaire PIMMS

Cette application fonctionne localement sur cette machine et peut être exposée publiquement via un tunnel temporaire.

## Démarrage simple

- Double-cliquer sur [start-online.cmd](/C:/Users/candi/Documents/Codex/2026-06-22/me-demander-si-tu-a-la/start-online.cmd)
- Vérifier l'état avec [status-online.cmd](/C:/Users/candi/Documents/Codex/2026-06-22/me-demander-si-tu-a-la/status-online.cmd)
- Arrêter proprement avec [stop-online.cmd](/C:/Users/candi/Documents/Codex/2026-06-22/me-demander-si-tu-a-la/stop-online.cmd)

## Auto-démarrage Windows

- Installer l'auto-lancement à l'ouverture de session avec [install-autostart.cmd](/C:/Users/candi/Documents/Codex/2026-06-22/me-demander-si-tu-a-la/install-autostart.cmd)
- Le retirer avec [remove-autostart.cmd](/C:/Users/candi/Documents/Codex/2026-06-22/me-demander-si-tu-a-la/remove-autostart.cmd)

## Liens et fichiers utiles

- Application locale : `http://127.0.0.1:8000`
- Tableau d'administration : `http://127.0.0.1:8000/?mode=tableau`
- URL publique courante : [public-url.txt](/C:/Users/candi/Documents/Codex/2026-06-22/me-demander-si-tu-a-la/instance/public-url.txt)
- Mot de passe admin : [admin_password.txt](/C:/Users/candi/Documents/Codex/2026-06-22/me-demander-si-tu-a-la/instance/admin_password.txt)
- Base de données : [pimms.sqlite3](/C:/Users/candi/Documents/Codex/2026-06-22/me-demander-si-tu-a-la/instance/pimms.sqlite3)

## Limites importantes

- L'URL publique est temporaire et peut changer si le tunnel redémarre.
- Si la machine est éteinte, en veille, hors ligne ou déconnectée, le service n'est plus accessible.
- Pour une solution vraiment permanente, il faut déplacer l'application vers un hébergement externe.
