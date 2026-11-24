# Mission d'exécution pour Claude — SAFYLIFE

## Objectif
Finaliser les cinq chantiers de **SAFYLIFE**, application PWA gratuite de préparation aux catastrophes, à partir du projet EXISTANT. **Ne pas réécrire l'application**, ne pas modifier le design validé et ne pas annoncer de fonctionnalités non démontrées.

## État existant (à vérifier indépendamment)
- Site déployé : https://tommyiboudghacene-sys.github.io/safylife-test/
- Archive PWA publiée dans ce dépôt : `SAFYLIFE_PWA.zip`. Workflow : `.github/workflows/publier-safylife.yml`.
- Code source complet, tests et rapport v0.11.0 : déjà disponibles dans la conversation Claude originale et dans le dossier Google Drive SAFYLIFE transmis auparavant. **Partir du code source complet, pas seulement du ZIP statique du dépôt.**
- Résultats rapportés au 24/11/2026 : 88/88 tests QA, 14/14 parcours Chromium hors connexion, accessibilité axe-core sans violation sur les pages auditées, 46 pays sur 237 avec numéros d'urgence sourcés, interface FR/EN/ES partielle.
- Retour utilisateur : installation et ouverture en mode avion sur son téléphone Android réussies. Cela ne prouve pas les fonctions GPS et téléphonie.

## Chantiers, dans cet ordre

### 1. SOS : fiabilité et absence de fausses promesses (priorité critique)
- Auditer le flux GPS : autorisé, refusé, délai dépassé, position imprécise, position inactive, absence de connexion, erreurs de partage.
- Vérifier les liens d'appel `tel:` et de SMS `sms:` sur les systèmes pris en charge sans composer de vrais numéros d'urgence. Prévoir tests manuels reproductibles sur Android et iOS, et expliciter ce qui ne peut être automatisé.
- Vérifier le comportement du bouton SOS en FR/EN/ES et sur mobile à petite largeur, avec accessibilité lecteur d'écran.
- Garantir affichage clair : **aucun appel, SMS ni alerte aux secours n'est automatiquement envoyé** ; l'utilisateur déclenche l'appel ou partage lui-même ses coordonnées.
- Aucune notification « alerte catastrophe officielle » fictive ; données sismiques USGS = observations, pas alertes de sécurité.

### 2. Traductions internationales, sécurité du contenu
- Terminer la couverture FR/EN/ES de l'interface, des guides et des scénarios, en gardant cohérence de navigation, langue déclarée et état hors connexion.
- **Ne pas traduire automatiquement puis présenter comme médicalement validées** des consignes de premiers secours. Produire des textes candidats avec référentiels officiels et une liste de validations expertes requises ; marquer explicitement les contenus en attente de validation.
- Contrôler longueur des textes, écran mobile, accessibilité, direction du texte et liens.

### 3. Numéros d'urgence, pays et maintenance
- Établir une base de données structurée pays/territoire/organisme/numéro, avec lien source officielle, date de consultation, niveau de confiance, date de révision et mécanisme d'échec sûr.
- Étendre la couverture au-delà des 46 pays déjà sourcés, prioriser les pays les plus peuplés et destinations fréquentes. Ne jamais deviner un numéro ou assimiler police/ambulance/pompiers s'ils diffèrent.
- Afficher clairement « numéro non vérifié » quand il n'existe pas de source fiable. Faire tests d'association pays → agence → numéro et cas frontières.

### 4. Compatibilité et PWA
- Tests automatisés de service worker, installation, cache, mise à jour de version, mode hors connexion, réouverture, petite taille d'écran, navigateurs Chromium/Firefox/WebKit selon disponibilité.
- Fournir un protocole de validation **sur vrais appareils** Android et iPhone (installation, démarrage hors réseau, GPS matériel, `tel:`, `sms:`, mise à jour PWA). Les tests matériels non réalisés doivent rester « non testés ».
- Performance, confidentialité, CSP, stockage et accessibilité (axe-core, navigation clavier, lecteurs d'écran quand possible).

### 5. Préparation à une diffusion internationale
- Réviser notices légales/confidentialité, sources des informations de prévention, mécanisme de mise à jour et historique des modifications. Ne pas inventer l'homologation, la validation médicale ni les partenariats institutionnels.
- Conserver la gratuité. Aucune dépense ni service payant, aucune API payante et aucune inscription externe sensible sans accord explicite.
- Évaluer les rappels calendrier existants ; ne pas promettre des notifications push ou une couverture temps réel sans infrastructure effectivement développée et testée.

## Méthode de livraison obligatoire
1. Inspecter l'archive source complète et le rapport de tests ; établir les écarts observables et prioriser risques/impact.
2. Corriger concrètement le code existant. Ajouter tests de non-régression et scénarios de défaillance. Conserver les fonctions déjà validées.
3. Exécuter tests et fournir sorties factuelles, listes de fichiers modifiés, preuves et limitations.
4. Travailler dans **une branche de développement dédiée**, ouvrir une demande de fusion pour revue ; **ne pas fusionner ni remplacer automatiquement le site public**.
5. Livrer les fichiers modifiés complets, la documentation de mise à jour, les sources officielles pays par pays et les validations humaines restant nécessaires.
6. Réaliser les parties techniquement possibles maintenant ; distinguer explicitement « réalisé et testé », « réalisé mais non testé sur appareil », « nécessite expert/validation humaine », « différé ».

## Critères de refus
- Aucun chiffre de réussite inventé ni aucune validation médicale déclarée sur simple examen IA.
- Aucune capture de données personnelles ou géolocalisation superflue.
- Ne jamais dégrader les fonctions SOS ou le mode avion.
- Pas de refonte de design ni de nouveau prototype parallèle.

**Ce ticket est une mission préparée pour Claude, pas une preuve que Claude l'a reçue ou exécutée.**