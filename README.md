# MiniNet — Projet ASA, M2 ALMA

Mini réseau social en console, conçu en composants et connecteurs. Python 3.10+ ; **aucune dépendance tierce à installer** pour lancer l'application, vérifier l'architecture ou exécuter les tests. SQLite est fourni par la bibliothèque standard des distributions Python habituelles.

## Démarrage

Ouvrir un terminal dans le dossier `MiniNet` (celui qui contient ce README).

```bash
python3 --version
python3 -m mininet --demo
```

Le mode démo initialise une base **en mémoire** (ne touche à aucun fichier de données). Comptes `alice`, `bob`, `clara`, mot de passe commun `Demo2026!`. Alice et Bob sont amis ; Bob a publié un texte et un lien, Clara a publié un texte hors du cercle d'amis. Bob a envoyé un message à Alice. Connectez-vous avec Alice (choix 2), consultez le fil (4) puis les messages (11).

Pour utiliser une base persistante, initialement vide :

```bash
python3 -m mininet
# ou choisir un fichier (le dossier parent doit exister)
python3 -m mininet --db mon_reseau.db
```

La base par défaut `mininet.db` est créée dans le répertoire courant ; les comptes, amitiés, publications et messages sont conservés entre deux exécutions. Ne supprimez pas la base si vous souhaitez conserver vos données. En Windows, remplacer `python3` par `py -3` ou `python` selon l'installation. Le terminal doit accepter UTF-8. Aucun serveur ou réseau nécessaire.

## Fonctionnement

À l'accueil, créer un compte (1), puis se connecter (2). Le mot de passe est masqué dans un terminal interactif ; il ne l'est pas lors d'une redirection d'entrée (pour les tests). Le pseudo est normalisé en minuscules ASCII (3 à 24 caractères), le mot de passe contient 8 à 128 caractères imprimables.

| Choix connecté | Fonction |
|---|---|
| 1, 2, 3 | Publier un texte (280 caractères), un lien HTTP(S) (500 caractères) ou une image locale (2 Mio max) |
| 4 | Fil chronologique inverse : soi-même et ses amis actuels |
| 5 | Exporter une image visible du fil par son numéro, vers un nouveau fichier |
| 6, 7, 8 | Ajouter, supprimer, lister les amis (relation réciproque immédiate) |
| 9 | Annuaire des autres comptes |
| 10, 11 | Envoyer un message privé (500 caractères) à un autre compte, lire les messages reçus/envoyés |
| 0 | Déconnexion ; 0 à l'accueil quitte le programme |

Pour publier une image de test, saisir `examples/mininet.png` au choix 3. Elle est copiée en base (BLOB), pas seulement référencée. Le fil indique son numéro et son nom ; le choix 5 permet de récupérer les octets. Saisir un fichier de destination inexistant, par exemple `image_exportee.png`. Les formats PNG, JPEG, GIF et WebP sont reconnus par signature ; aucun affichage graphique ou décodage intégral n'est réalisé. Les liens ne sont jamais téléchargés ni ouverts automatiquement.

Les notifications de nouveaux messages sont affichées une seule fois lors du prochain affichage du menu du destinataire, durant le même processus. Les messages restent disponibles après redémarrage, même si les notifications en mémoire disparaissent. Le modèle de confiance est celui d'un processus local : les comptes isolent les données à travers la console, pas vis-à-vis d'un administrateur ayant accès au fichier SQLite.

## Vérifications

```bash
python3 -m unittest discover -v
python3 tools/architecture.py --check
```

Les tests créent leurs propres bases temporaires et n'altèrent pas les données utilisateur. `docs/RESULTATS_TESTS.txt` contient la sortie d'une exécution réelle. Les tests contrôlent les comportements et le câblage, pas seulement le démarrage. Voir le rapport pour les limites de la validation.

## Structure et livrables

- `mininet/components/` : sept composants (console, utilisateurs, amis, posts, messages, notifications et stockage).
- `mininet/architecture.py` : modèle déclaratif des ports, opérations et liaisons ; `assembly.py` : assemblage ; `connectors.py` : appels synchrones et publish/subscribe.
- `architecture/MiniNet.acme` : description ADL ; `composants.svg` / `.png` : vue C&C ; `TRACABILITE.md` : correspondance code, ports et rôles.
- `docs/Rapport_architecture.pdf` : rapport (9 pages) ; `docs/Soutenance.pptx` et `docs/Soutenance.pdf` : support ; `docs/DEMONSTRATION.md` : scénario et préparation orale.
- `tests/` : tests fonctionnels, architecturaux et de bout en bout ; `examples/` : image exemple.

Pour régénérer les vues textuelles après une modification du modèle :

```bash
python3 tools/architecture.py
# Graphviz facultatif, uniquement pour régénérer les images déjà livrées :
dot -Tpng -Gdpi=180 architecture/composants.dot -o architecture/composants.png
dot -Tsvg architecture/composants.dot -o architecture/composants.svg
```

La spécification ACME utilise le sous-ensemble structurel (System, Component, Port, Connector, Role, Attachments). La vérification locale contrôle la synchronisation de la vue générée et le câblage effectif, mais n'est pas un compilateur ACME généraliste. Références : Carnegie Mellon University, [Acme Language Overview](https://www.cs.cmu.edu/~acme/docs/language_overview.html) et [grammaire du parseur Armani](https://www.cs.cmu.edu/~acme/html/ArmaniParser.html).

## Avant le rendu

Compléter les noms du binôme sur le support et la page de garde si requis (sources documentaires facultatives dans `tools/doc_sources/`). Relire le rapport, exécuter les commandes ci-dessus, répéter la démonstration et pouvoir expliquer les choix. Le prototype est volontairement local, mono-processus et non conçu pour une mise en production.
