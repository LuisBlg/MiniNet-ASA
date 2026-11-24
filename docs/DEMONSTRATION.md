# Soutenance — déroulé conseillé (12 à 14 minutes)

Les diapositives sont un support, pas un texte à réciter. Les deux membres peuvent se répartir l'architecture (diapos 1 à 4) et l'implémentation / démonstration (5 à 8).

## 1. Présentation (6 à 7 minutes)

| Diapo | Durée | Points à expliquer |
|---|---:|---|
| 1 | 45 s | Petit réseau social ; objectif = architecture, pas interface graphique. |
| 2 | 1 min | Les cinq exigences, amis réciproques, messages séparés du fil. |
| 3 | 1 min 30 | Sept composants, neuf appels et un bus. Rectangle = composant, ellipse = connecteur. |
| 4 | 1 min | Ports requis/fournis, rôles caller/callee, deux attaches, exemple ACME. |
| 5 | 1 min | `architecture.py` → `assembly.py` → composants ; même modèle → ACME. |
| 6 | 1 min | Message persisté puis événement synchrone ; destinataire seul notifié. |

## 2. Démonstration (4 à 5 minutes)

Depuis le dossier racine : `python3 -m mininet --demo`. Chaque ligne ci-dessous correspond à une saisie suivie d'Entrée. Mot de passe de démo : `Demo2026!`.

| Étape | Saisies successives | Résultat à montrer |
|---|---|---|
| A | `2`, `alice`, `Demo2026!`, `4` | Notification initiale et fil avec le texte/lien de Bob, pas celui de Clara. |
| B | `11`, `8` | Message privé de Bob et liste d'amis. |
| C | `3`, `examples/mininet.png`, `4` | Publication image n°4 (dans une démo fraîche). |
| D | `10`, `bob`, `Démo : message privé`, `0` | Envoi et déconnexion. |
| E | `2`, `bob`, `Demo2026!`, `11`, `4` | Notification ciblée, message reçu, image d'Alice visible. |
| F | `5`, `4`, `mon_export.png` | Export de l'image (choisir un fichier qui n'existe pas). |
| G | `7`, `alice`, `4`, `0` | Après suppression d'Alice, son image disparaît du fil de Bob. |
| H | `2`, `clara`, `Demo2026!`, `11`, `4`, `0`, `0` | Aucun message privé des autres ; Clara ne voit que sa propre publication. |

Si l'export existe déjà, saisir un autre chemin. Pour démontrer une création de compte ou la persistance, lancer le mode `--db demo_locale.db` (nom de fichier neuf), créer un compte, quitter puis se reconnecter. Ne pas confondre avec `--demo`, qui est volontairement éphémère.

## 3. Conformité et conclusion (2 minutes)

- Ouvrir `architecture/MiniNet.acme` et `mininet/architecture.py` côte à côte.
- Dans `mininet/assembly.py`, montrer la création de `ProcedureCall` pour chaque liaison et l'abonnement `bus.subscribe(...)`.
- Montrer `mininet/components/messages.py` : la publication d'événement a lieu après le stockage ; aucune dépendance directe vers les notifications.
- Exécuter `python3 tools/architecture.py --check`, puis `python3 -m unittest discover -v` (ou afficher le journal de test livré si manque de temps).
- Conclure : toutes les fonctions du sujet sont couvertes ; extension publish/subscribe ; pas d'infrastructure inutile.

## Questions probables

**Pourquoi Python et une console ?** Le sujet autorise la console ; Python facilite le prototype et SQLite évite un serveur externe. Les connecteurs sont néanmoins des objets distincts et les opérations autorisées sont explicites.

**En quoi un connecteur diffère-t-il d'un composant ?** Un composant réalise un traitement ou conserve des données ; le connecteur matérialise une interaction. `ProcedureCall` relaie les opérations autorisées ; `MessageBus` distribue un événement.

**Pourquoi le bus est-il synchrone ?** Pas de thread, pas de course ni de broker. Publish/subscribe désigne le découplage émetteur/abonnés et n'implique pas nécessairement l'asynchronisme. L'émetteur ne connaît pas NotificationService. Une panne de callback après commit peut laisser le message enregistré sans notification.

**Pourquoi les amis sont-ils symétriques ?** C'est une décision fonctionnelle minimale, non imposée par le sujet. Un seul couple ordonné est stocké ; les deux utilisateurs voient la relation immédiatement.

**Comment est protégée la confidentialité ?** La console prend l'identité du compte connecté ; les requêtes fil/export et messages sélectionnent les données autorisées. Les mots de passe sont salés et dérivés. Le fichier SQLite n'est pas chiffré, et les composants internes supposent un appelant de confiance.

**Pourquoi la conformité n'est-elle pas seulement documentaire ?** Les liaisons du modèle déterminent l'injection réelle des ports et génèrent la vue ACME. Des tests inspectent les instances, le fournisseur, les opérations exposées et l'abonnement. Ce n'est pas une preuve formelle exhaustive ni une validation par AcmeStudio.

**Comment évoluer vers un service web ?** Remplacer ConsoleUI par un adaptateur HTTP avec gestion de sessions et contrôles d'accès ; définir une nouvelle configuration, vérifier ses ports et adapter les tests. Un bus asynchrone durable nécessiterait des garanties supplémentaires (retry, idempotence, outbox).
