# SAFYLIFE — lot de fiabilisation v0.12.0-dev.1

**Date : 24 novembre 2026 · État : version de développement, NON publiée.**

## Base de travail

Code repris du fichier source v0.11.0 corrigé par Claude, livré dans
`SAFYLIFE_CLAUDE_VERIFIED/SAFYLIFE_PROJET_COMPLET.zip`, sans refonte graphique.
Le site public reste sur le lot v0.11.0 tant que les modifications de la branche
ne sont pas validées et fusionnées explicitement.

## Corrections réalisées

1. Un même bouton GPS ne déclenche plus plusieurs demandes simultanées ; il est
   temporairement désactivé durant l'acquisition.
2. Après navigation ou remplacement de l'écran, la réponse GPS tardive ne peut
   plus réafficher l'ancien écran SOS. Coordonnées invalides refusées avant stockage.
3. L'API Web Share peut échouer (NotAllowedError, indisponibilité) : la copie est
   tentée, puis un champ sélectionnable est affiché si elle échoue. Une fermeture
   volontaire du menu de partage (AbortError) n'entraîne pas de copie automatique.
4. Les numéros de police différenciés mobile/fixe en français sont maintenant
   différenciés également en anglais et espagnol. Les liens de sources de ces
   numéros complémentaires sont présents dans ces trois langues.
5. Ajout d'un audit structurel hors ligne des numéros enregistrés et d'une notice
   précisant la confidentialité, les limites de l'hébergement et des fonctions SOS.
6. Deux nouveaux modules isolent le GPS et le partage, et sont ajoutés au cache PWA.

## Tests exécutés et résultats

- Compilation TypeScript (`tsc -p tsconfig.json`) : réussite.
- Compilation des tests TypeScript (`tsc -p tsconfig.test.json`) : réussite.
- Suite Node (`node --test "build/tests/**/*.test.js"`) : **94/94**, contre 88/88
  dans la version source reçue. Les six nouveaux tests couvrent les résultats GPS,
  les erreurs, le partage, la copie et l'annulation volontaire.
- `node scripts/check-offline.mjs` : **59 ressources de cache présentes**.
- `node scripts/test-service-worker.mjs` : installation simulée, cache,
  isolement du périmètre, mode hors connexion simulé et exclusions des requêtes
  privées : réussite.
- `node scripts/build-single-html.mjs` et `node scripts/test-single-html.mjs` : réussite.
- Chromium `scripts/test-sos-regression-dom.py` : parcours de régression SOS
  **FR/EN/ES réussis** (GPS simulé, demandes simultanées, sortie d'écran,
  copie manuelle après refus du partage) ; 0 erreur JavaScript sur ces parcours.
- `scripts/audit-emergency-sources.mjs` : vérification structurelle des numéros,
  catégories et liens de sources, sans vérification en ligne du fond des sources.

## Contrôles non aboutis / limites

- Test HTTP local + vrai service worker sur Chromium bloqué par la politique
  d'accès de cet environnement : `net::ERR_BLOCKED_BY_ADMINISTRATOR`.
  Cela ne signifie **pas** que SAFYLIFE est défectueux ; cela ne valide pas non plus
  le fonctionnement du service worker réel sur le nouveau lot.
- Pas de test sur iPhone réel, pas de test GPS matériel, pas d'appel ni SMS réel.
  L'utilisateur a validé précédemment l'installation et le mode avion sur Android
  pour l'ancienne version publique, pas pour ce lot de développement.
- Les numéros d'urgence n'ont pas tous été revérifiés pays par pays. Les pays
  sans numéros sourcés restent sans numéro affiché.
- Traductions des fiches de premiers secours : non modifiées, en attente de
  relecture médicale qualifiée. Aucun système de notifications officielles
  temps réel ni envoi automatique de SOS n'a été développé.
- Les tests Android et iOS d'ouverture de l'application SMS et de partage natif
  doivent être réalisés sur appareils physiques avant diffusion à grande échelle.

## Déploiement sûr

Ce lot se propose dans une branche GitHub séparée. Le ZIP de site statique de
production `SAFYLIFE_PWA.zip` situé sur la branche principale **n'est pas
remplacé**. Après validation, remplacer cette archive par le ZIP PWA du lot et
laisser le workflow GitHub Pages existant publier la nouvelle version.
