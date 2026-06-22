# Mise en ligne permanente

Le projet est prêt pour un déploiement durable sur un hébergeur externe.

## Cible préparée

Le fichier [render.yaml](/C:/Users/candi/Documents/Codex/2026-06-22/me-demander-si-tu-a-la/render.yaml) prépare un déploiement Render avec :

- un service web Python ;
- un healthcheck sur `/api/health` ;
- une base SQLite déplacée sur disque persistant via `PIMMS_DB_PATH=/var/data/pimms.sqlite3` ;
- des variables sensibles à renseigner dans l'interface Render.

## Ce qu'il manque pour terminer vraiment

Il manque uniquement l'accès à un compte d'hébergement :

- compte Render ;
- dépôt GitHub/GitLab/Bitbucket connecté à Render ;
- éventuel domaine personnalisé si tu veux une URL définitive.

## Chemin recommandé

1. Publier ce dossier dans un dépôt Git.
2. Créer un Web Service sur Render à partir de ce dépôt.
3. Vérifier que `ADMIN_PASSWORD` et `MEDIATOR_URL` sont bien renseignés.
4. Ajouter le disque persistant `/var/data`.
5. Tester :
   - `/`
   - `/?mode=tableau`
   - `/api/health`
   - `/api/reporting/export.csv`

## Important

- La version tunnel actuelle reste pratique pour tester, mais elle n'est pas une URL permanente.
- La version Render préparée ici suppose un plan compatible disque persistant.
