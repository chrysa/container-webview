<<<<<<< HEAD

# web GUI for managing docker compose project

||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")

# web GUI for managing docker compose project dev

generate graph for docker-compose
=======

# Docker Overview WebUI

Interface web pour gérer et visualiser vos projets Docker Compose — topologie interactive, métriques en temps réel, alertes et gestion du cycle de vie des services.
>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")

---

## Table des matières

- [Docker Overview WebUI](#docker-overview-webui)
    - [Table des matières](#table-des-matières)
    - [Fonctionnalités](#fonctionnalités)
    - [Architecture](#architecture)
    - [Prérequis](#prérequis)
    - [Démarrage rapide](#démarrage-rapide)
    - [Configuration](#configuration)
    - [Endpoints API](#endpoints-api)
    - [Commandes Make](#commandes-make)
    - [Tests](#tests)
    - [Roadmap](#roadmap)

<<<<<<< HEAD

- [web GUI for managing docker compose project](#web-gui-for-managing-docker-compose-project)
    - [Table Of Content](#table-of-content)
    - [SPECS / Cahier des charges](#specs--cahier-des-charges)
        - [Introduction](#introduction)
        - [Fonctionnalités principales](#fonctionnalit%C3%A9s-principales)
            - [Visualisation graphique](#visualisation-graphique)
            - [Configuration personnalisable](#configuration-personnalisable)
            - [Recherche et filtrage](#recherche-et-filtrage)
            - [Autodétection des fichiers Docker Compose](#autod%C3%A9tection-des-fichiers-docker-compose)
            - [Personnalisation du thème et du logo](#personnalisation-du-th%C3%A8me-et-du-logo)
            - [Fichier de configuration du projet](#fichier-de-configuration-du-projet)
            - [Utilisation du moteur de rendu JSX](#utilisation-du-moteur-de-rendu-jsx)
            - [Gestion des erreurs](#gestion-des-erreurs)
            - [Tableau de bord](#tableau-de-bord)
            - [Menu horizontal et menu latéral](#menu-horizontal-et-menu-lat%C3%A9ral)
        - [Utilisation](#utilisation)
        - [Liste des évolutions possibles](#liste-des-%C3%A9volutions-possibles)
            - [Intégration Docker Swarm](#int%C3%A9gration-docker-swarm)
            - [Intégration avec d'autres outils DevOps](#int%C3%A9gration-avec-dautres-outils-devops)
            - [Support d'autres formats de configuration](#support-dautres-formats-de-configuration)
            - [Visualisation des dépendances entre services](#visualisation-des-d%C3%A9pendances-entre-services)
            - [Analyse des performances](#analyse-des-performances)
            - [Notifications et alertes](#notifications-et-alertes)
            - [Versioning et historique des configurations](#versioning-et-historique-des-configurations)
            - [Mode collaboratif](#mode-collaboratif)
            - [Intégration avec des services de gestion des secrets externes](#int%C3%A9gration-avec-des-services-de-gestion-des-secrets-externes)
            - [Optimisation des performances](#optimisation-des-performances)
            - [Support multi-projets](#support-multi-projets)
            - [Internationalisation](#internationalisation)
        - [Roadmap](#roadmap)
            - [Version 1.0](#version-10)
            - [Version 2.0](#version-20)
            - [Version 3.0](#version-30)
            - [Version 4.0](#version-40)
            - [Version 5.0](#version-50)
        - [Plan de développement](#plan-de-d%C3%A9veloppement)
            - [Mise en place du projet](#mise-en-place-du-projet)
            - [Création des composants de base](#cr%C3%A9ation-des-composants-de-base)
            - [Gestion des fichiers Docker Compose](#gestion-des-fichiers-docker-compose)
            - [Configuration personnalisable](#configuration-personnalisable-1)
            - [Recherche et filtrage](#recherche-et-filtrage-1)
            - [Amélioration de la visualisation graphique](#am%C3%A9lioration-de-la-visualisation-graphique)
            - [Tableau de bord](#tableau-de-bord-1)
            - [Gestion des erreurs](#gestion-des-erreurs-1)
            - [Intégration Docker Registry](#int%C3%A9gration-docker-registry)
            - [Personnalisation du thème et du logo](#personnalisation-du-th%C3%A8me-et-du-logo-1)
            - [Gestion des secrets](#gestion-des-secrets)
            - [Export graphique paramétrable en PNG](#export-graphique-param%C3%A9trable-en-png)
            - [Export des configurations au format tableau](#export-des-configurations-au-format-tableau)
        - [Liste de références](#liste-de-r%C3%A9f%C3%A9rences)
        - [Conseils](#conseils)
    - [IDEAS](#ideas)
    - [Makefile](#makefile)
||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
- [web GUI for managing docker compose project dev](#web-gui-for-managing-docker-compose-project-dev)
    - [Table Of Content](#table-of-content)
    - [TO FIX](#to-fix)
    - [TODO](#todo)
        - [WEbUI](#webui)
    - [Makefile](#makefile)
=======

---
>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")

## Fonctionnalités

<<<<<<< HEAD

## SPECS / Cahier des charges

||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")

## TO FIX

=======

- **Vue d'ensemble** — liste tous les projets Compose détectés dans le répertoire configuré
- **Topologie** — graphe interactif des services et réseaux d'un projet
- **Métriques** — CPU, mémoire et réseau en temps réel par conteneur
- **Alertes** — détection automatique des conteneurs en anomalie (exited, restarting, unhealthy)
- **Cycle de vie** — start / stop / restart / pause / unpause depuis l'interface
- **Authentification** — JWT Bearer, fallback local + LDAP optionnel

>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")

<<<<<<< HEAD

### Introduction

||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")

## TODO

=======
---
>>>>>>>
>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")

<<<<<<< HEAD
Le projet Docker Compose Overview vise à fournir un outil convivial pour visualiser et gérer des projects Docker Compose. L'application offrira une interface graphique interactive permettant aux utilisateurs de mieux comprendre la structure et les dépendances des services, réseaux, secrets, configs, volumes, et autres clés définies dans les fichiers Docker Compose. Le projet sera développé en utilisant ReactJS avec le moteur de rendu JSX pour faciliter la création de composants réutilisables.

### Fonctionnalités principales

#### Visualisation graphique

L'application permettra aux utilisateurs de visualiser les services, réseaux, secrets, configs, volumes, et autres clés définies par les standards de Docker Compose, sous forme d'un graphique interactif. Le graphique offrira une représentation claire et intuitive de la structure du projet. Dans le graphique, les services et les relations entre eux seront clairement représentés, et des informations supplémentaires telles que les configurations de services, les ports exposés, et les variables d'environnement seront affichées au besoin.

#### Configuration personnalisable

L'application sera hautement configurable à l'aide d'un fichier de configuration YAML. Les utilisateurs pourront personnaliser divers aspects de l'application tels que les couleurs, les thèmes, les filtres, et les paramètres par défaut. Les configurations personnalisées seront chargées à partir du fichier `overview-config.yaml`, situé dans le dossier `config` à la racine du projet à analyser, les valeurs par default elles seront stockées dans un fichier default/config/overview-config-default.yaml dans le projet Docker Compose Overview.

#### Recherche et filtrage

L'application offrira des fonctionnalités de recherche et de filtrage pour permettre aux utilisateurs de trouver rapidement des services spécifiques, de filtrer les services par réseau ou par volume, et d'appliquer des filtres personnalisés.

#### Autodétection des fichiers Docker Compose

L'application détectera automatiquement les fichiers Docker Compose présents dans le dossier, mais l'utilisateur pourra également spécifier les fichiers directement dans la configuration s'il le souhaite.

#### Personnalisation du thème et du logo

Les utilisateurs auront la possibilité de personnaliser le thème et le logo de l'application, ainsi que le positionnement du menu. Cette personnalisation pourra être mise à jour directement depuis l'interface utilisateur.

#### Fichier de configuration du projet

Le fichier de configuration du projet `overview-config-project.yaml` se trouvera à la racine du projet à analyser, et il permettra de définir les configurations spécifiques pour le projet en cours.

#### Utilisation du moteur de rendu JSX

Le projet sera développé en utilisant le moteur de rendu JSX pour séparer le code JavaScript et HTML et faciliter le développement de composants réutilisables.

#### Gestion des erreurs

L'application fournira une gestion des erreurs améliorée pour fournir des messages d'erreur plus informatifs et guider les utilisateurs en cas de problème. Des indications claires seront fournies en cas d'erreur de chargement de fichiers Docker Compose ou de mauvaises configurations.

#### Tableau de bord

L'application disposera d'un tableau de bord offrant des statistiques détaillées sur les services, réseaux, secrets, configs, volumes, et autres clés du projet Docker. Les utilisateurs pourront visualiser des graphiques, des métriques, et des informations essentielles pour une meilleure compréhension de l'état du projet.

#### Menu horizontal et menu latéral

Par défaut, le menu horizontal permettra d'accéder aux fonctions globales de navigation et d'édition des fichiers Docker Compose. Le menu latéral contiendra les filtres par défaut pour les réseaux et les volumes, et il pourra être paramétré suivant une liste prédéfinie. Lorsqu'un service est sélectionné, l'éditeur de Docker Compose se centrera sur le service sélectionné, même en présence de plusieurs fichiers Docker Compose.

### Utilisation

le project est dans un container docker et est utilise en montant le projet a analyser sous forme d'un volume

### Liste des évolutions possibles

#### Intégration Docker Swarm

Une évolution future du projet pourrait inclure l'intégration de la gestion de services Docker Swarm dans l'application, permettant ainsi aux utilisateurs de visualiser et de gérer des déploiements Docker Swarm.

#### Intégration avec d'autres outils DevOps

Permettre l'intégration de l'application avec d'autres outils DevOps populaires tels que Jenkins, GitLab CI/CD, ou Travis CI. Cela permettrait d'obtenir une vue globale des projets et de faciliter les déploiements.

#### Support d'autres formats de configuration

Actuellement, l'application se concentre sur les fichiers Docker Compose au format YAML, mais il pourrait être intéressant d'étendre le support à d'autres formats de configuration tels que JSON, TOML, ou HCL.

#### Visualisation des dépendances entre services

Ajouter la possibilité d'afficher graphiquement les dépendances entre les différents services du projet Docker Compose. Cela permettrait aux utilisateurs de mieux comprendre les interactions entre les services et d'identifier les éventuelles dépendances circulaires.

#### Analyse des performances

Intégrer des fonctionnalités d'analyse des performances pour évaluer les performances des services Docker et identifier les goulots d'étranglement.

#### Notifications et alertes

Mettre en place des notifications et des alertes pour avertir les utilisateurs en cas de problèmes dans le projet Docker Compose, tels que des erreurs de configuration ou des services défaillants.

#### Versioning et historique des configurations

Permettre aux utilisateurs de conserver un historique des configurations personnalisées et de revenir à des versions précédentes si nécessaire.

#### Mode collaboratif

Ajouter un mode collaboratif qui permettrait à plusieurs utilisateurs de travailler simultanément sur le même projet Docker Compose et de partager leurs configurations.

#### Intégration avec des services de gestion des secrets externes

Permettre l'intégration avec des services externes de gestion des secrets, tels que HashiCorp Vault, pour renforcer la sécurité des données sensibles dans les fichiers Docker Compose.

#### Optimisation des performances

Améliorer les performances de l'application pour gérer efficacement les projets Docker Compose de grande envergure avec un grand nombre de services et de configurations.

#### Support multi-projets

Étendre l'application pour prendre en charge la gestion de plusieurs projets Docker Compose à partir d'une seule interface et d'une plateforme centralisee.

#### Internationalisation

Ajouter la prise en charge de plusieurs langues pour rendre l'application accessible à une audience internationale.

### Roadmap

La roadmap du projet Docker Compose Overview sera itérative, avec des mises à jour régulières pour ajouter de nouvelles fonctionnalités et améliorer l'expérience utilisateur. Voici une proposition de roadmap initiale :

#### Version 1.0

- Visualisation graphique des services, réseaux, secrets, configs, volumes, et autres clés Docker Compose.
- Gestion de plusieurs fichiers Docker Compose.
- Configuration personnalisable à l'aide du fichier `overview-config-project.yaml`.
- Recherche et filtrage des services.
- Interface utilisateur de base avec barre de navigation, en-tête, et barre latérale personnalisables.

#### Version 2.0

- Ajout d'informations supplémentaires dans les nœuds du graphique.
- Exportation et importation de configurations personnalisées.
- Intégration des services Docker Swarm.

#### Version 3.0

- Gestion des erreurs améliorée.
- Tableau de bord avec des statistiques sur les services, réseaux, secrets, configs, volumes, et autres clés du projet Docker.

#### Version 4.0

- Intégration de Docker Registry.
- Améliorations de l'interface utilisateur, y compris la personnalisation des thèmes, des logos, et du positionnement du menu.

#### Version 5.0

- Intégration de la gestion des secrets Docker.

### Plan de développement

Voici un plan de développement préliminaire pour le projet Docker Compose Overview

#### Mise en place du projet

- Création de la structure de fichiers.
- Configuration de l'environnement de développement.
- Installation des dépendances (React, Material-UI, etc.).
- Création du fichier `overview-config-project.yaml` à la racine du projet à analyser.

#### Création des composants de base

- Création du composant de visualisation graphique avec le graphique interactif.
- Mise en place du composant de barre de navigation.
- Création du composant de barre latérale pour les filtres.

#### Gestion des fichiers Docker Compose

- Mise en place de la détection automatique des fichiers Docker Compose dans le dossier.
- Implémentation de la possibilité de spécifier les fichiers directement dans la configuration.

#### Configuration personnalisable

- Lecture du fichier `overview-config-project.yaml` pour charger les configurations personnalisées.
- Création d'un formulaire de configuration pour permettre à l'utilisateur de personnaliser l'application.

#### Recherche et filtrage

- Mise en place des fonctionnalités de recherche et de filtrage pour faciliter la navigation dans les fichiers Docker Compose.

#### Amélioration de la visualisation graphique

- Ajout d'informations supplémentaires dans les nœuds du graphique (port, environnement, etc.).

#### Tableau de bord

- Création du tableau de bord avec des statistiques sur les services, réseaux, secrets, configs, volumes, et autres clés du projet Docker.

#### Gestion des erreurs

- Amélioration de la gestion des erreurs pour une expérience utilisateur plus fluide.

#### Intégration Docker Registry

- Mise en place de l'intégration Docker Registry pour afficher les images Docker utilisées dans le projet.

#### Personnalisation du thème et du logo

```
- Implémentation de la possibilité de personnaliser le thème, le logo, et le positionnement du menu.
```

#### Gestion des secrets

```
- Intégration de la gestion des secrets Docker pour sécuriser les informations sensibles.
```

#### Export graphique paramétrable en PNG

```
- Ajout de la possibilité d'exporter le graphique interactif au format PNG avec des paramètres personnalisables (taille, qualité, etc.).
```

#### Export des configurations au format tableau

```
- Ajout de la possibilité 'exporter les configurations personnalisées sous forme de tableau pour faciliter leur visualisation et leur partage.
```

### Liste de références

1. Documentation React : <https://reactjs.org/docs/getting-started.html>
1. Documentation Material-UI : <https://material-ui.com/getting-started/installation/>
1. Documentation YAML : <https://yaml.org/spec/1.2/spec.html>
1. Documentation Docker Compose : <https://docs.docker.com/compose/>

### Conseils

- Organisez le code en utilisant des composants réutilisables pour faciliter la maintenance et les mises à jour futures.
- Testez régulièrement l'application pour vérifier son bon fonctionnement et détecter les erreurs le plus tôt possible.
- Implémentez des messages d'erreur et des indications pour guider les utilisateurs lors de l'utilisation de l'application.
- Soyez attentif aux commentaires et aux retours des utilisateurs pour améliorer l'expérience utilisateur.
- Considérez l'intégration continue et le déploiement continu pour faciliter le processus de développement et de déploiement de l'application.

______________________________________________________________________

Je vous présente donc le projet Docker Compose Overview, un outil puissant et convivial pour visualiser et gérer les fichiers Docker Compose dans un projet Docker. Grâce à son interface graphique interactive, les utilisateurs pourront mieux comprendre la structure et les dépendances des services, réseaux, secrets, configs, volumes et autres clés définis dans les fichiers Docker Compose.

Le cahier des charges détaille les principales fonctionnalités du projet, notamment la visualisation graphique, la configuration personnalisable, la recherche et le filtrage, l'intégration Docker Swarm, la personnalisation du thème et du logo, et bien plus encore. Le projet sera développé en utilisant ReactJS avec le moteur de rendu JSX pour offrir une expérience utilisateur fluide et faciliter le développement de composants réutilisables.

La roadmap du projet prévoit des mises à jour itératives pour ajouter de nouvelles fonctionnalités et améliorer l'expérience utilisateur. Des évolutions futures sont également envisagées, telles que l'intégration avec d'autres outils DevOps, la visualisation des dépendances entre services, l'analyse des performances, la gestion des secrets et bien d'autres.

Le plan de développement détaille les étapes pour la création du projet, allant de la mise en place du projet à l'intégration de fonctionnalités avancées telles que le tableau de bord et la gestion des erreurs.

Le projet suivra une approche Agile, avec des mises à jour régulières et des feedbacks utilisateurs pour assurer une évolution continue et répondre aux besoins changeants des utilisateurs.

Enfin, le projet utilisera TypeScript pour bénéficier des avantages de la vérification statique des types, ce qui améliorera la qualité du code et facilitera la collaboration entre les développeurs.

Je suis enthousiaste à l'idée de développer ce projet, et j'attends avec impatience vos retours et suggestions pour le faire évoluer vers un outil de gestion Docker complet et performant. Merci de votre attention, et n'hésitez pas à poser des questions ou à donner votre avis sur ce projet prometteur.

## IDEAS

- manage project dynamicly from graph
- create/update service from GUI
- export docker compose
    - global
    - splitted by service
    - dev and prod
- launch makefile rules
- add cli/web GUI for services management functionalities from composes files
    - build selected services
    - generate graphs
    - interact with graphs
    - run selected services
    - remove selected services
    - logs access selected services
    - up selected services
    - stats selected services
    - add notification on docker container state modification on project
- add web IDE
- add project overview
- add browser and desktop notificatilons
- add companion IA companion to debug
- possibility to deploy in registries
- git management
- ci-support and management
- make docker desktop extenssion

## Makefile

<!-- START makefile-doc -->
||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")

### WEbUI

- manage project dynamicly from graph
- create/update service from GUI
- export docker compose
    - global
    - splitted by service
    - dev and prod
- launch makefile rules
- add cli/web GUI for services management functionalities from composes files
    - build selected services
    - generate graphs
    - interact with graphs
    - run selected services
    - remove selected services
    - logs access selected services
    - up selected services
    - stats selected services
    - add notification on docker container state modification on project
- add web IDE
- add project overview
- add browser and desktop notificatilons
- add companion IA companion to debug
- possibility to deploy in registries
- git management
- ci-support and management
- make docker desktop extenssion

## Makefile

<!-- START makefile-doc -->
=======

## Architecture
>>>>>>>
>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")

```
<<<<<<< HEAD
$ make help
make[1]: Entering directory '/home/anthony/Documents/perso/projects/docker-overview-webui'
Hello to the `docker-overview-webui` Makefile
 	make [target] [args]


| Rule                                               | Help                                                         | Usage                                              | dependencies                                                 | Service              |
+====                                                +====                                                          +====                                                +====                                                          +====                  +
| help                                               | display help                                                 |                                                    |                                                              |                      |
| app-build                                          | build application                                            |                                                    |                                                              |                      |
| app-clean                                          |                                                              |                                                    |                                                              |                      |
| app-dev                                            | launch as dev                                                |                                                    |                                                              |                      |
| app-prod                                           | launch as prod                                               |                                                    |                                                              |                      |
| app-test                                           |                                                              |                                                    |                                                              |                      |
| docker-build                                       | build image                                                  |                                                    |                                                              |                      |
| docker-connect-dev                                 | connect-to-dev-server                                        |                                                    |                                                              |                      |
| docker-stop                                        | stop services                                                |                                                    |                                                              |                      |
| docker-up-detach                                   |                                                              |                                                    |                                                              |                      |
| node-upgradable-package                            | check outdated packages                                      |                                                    |                                                              |                      |
| ci-run-local                                       | run ci pipeline locally                                      |                                                    |                                                              |                      |
| pre-commit                                         | run localy precommit                                         |                                                    |                                                              |                      |
make[1]: Leaving directory '/home/anthony/Documents/perso/projects/docker-overview-webui'
||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
$ make help
make[1]: Entering directory '/mnt/d/drive/dev/repos/-perso-/docker-overview-webui'
Hello to the `docker-overview-webui` Makefile
 	make [target] [args]


| Rule                                               | Help                                                         | Usage                                              | dependencies                                                 | Service              |
+====                                                +====                                                          +====                                                +====                                                          +====                  +
| help                                               | display help                                                 |                                                    |                                                              |                      |
| docker-build                                       | build image                                                  |                                                    |                                                              |                      |
| docker-connect-dev                                 | connect-to-dev-server                                        |                                                    |                                                              |                      |
| docker-stop                                        | stop services                                                |                                                    |                                                              |                      |
| docker-up                                          | up service                                                   |                                                    |                                                              |                      |
| docker-up-detach                                   | up service and detach                                        |                                                    |                                                              |                      |
| node-upgradable-package                            | check outdated packages                                      |                                                    |                                                              |                      |
| node-dev-upgradable-package                        | check outdated packages on dev                               |                                                    |                                                              |                      |
| app-build                                          | build application                                            |                                                    |  app-install-deps                                            |                      |
| app-install-deps                                   | install proect dependencies locally                          |                                                    |                                                              |                      |
| app-dev                                            | launch as dev                                                |                                                    |  app-install-deps                                            |                      |
| ci-run-local                                       | run ci pipeline locally                                      |                                                    |                                                              |                      |
| pre-commit                                         | run localy precommit                                         |                                                    |                                                              |                      |
make[1]: Leaving directory '/mnt/d/drive/dev/repos/-perso-/docker-overview-webui'
=======
docker-overview-webui/
├── api/                        # Backend FastAPI (Python 3.12)
│   ├── app/
│   │   ├── config.py           # Configuration via pydantic-settings
│   │   ├── constants.py        # Constantes (StrEnum, Final)
│   │   ├── main.py             # App FastAPI + CORS + routeurs
│   │   ├── security.py         # Service JWT
│   │   ├── routers/            # Contrôleurs HTTP (minces)
│   │   │   ├── auth.py         # POST /api/auth/login, GET /api/auth/check
│   │   │   ├── projects.py     # GET /api/projects[/{id}]
│   │   │   ├── topology.py     # GET /api/projects/{id}/topology
│   │   │   ├── lifecycle.py    # POST /api/projects/{id}/services/{svc}/{action}
│   │   │   ├── metrics.py      # GET /api/projects/{id}/metrics
│   │   │   ├── alerts.py       # GET /api/alerts[/project/{id}]
│   │   │   └── logs.py         # WebSocket /api/projects/{id}/services/{svc}/logs
│   │   ├── services/           # Logique métier
│   │   │   ├── auth_service.py
│   │   │   ├── docker_client.py
│   │   │   ├── project_manager.py
│   │   │   ├── lifecycle_service.py
│   │   │   ├── metrics_service.py
│   │   │   ├── alerts_service.py
│   │   │   └── topology_service.py
│   │   └── tests/              # pytest — services + routers
│   ├── pyproject.toml          # Dépendances + ruff + mypy + pytest + coverage
│   └── Dockerfile              # Stages: base / dev / test / production
├── code/                       # Frontend React 18 + Vite + TypeScript
│   └── src/
├── docker-compose.yml          # Stack de développement
├── Makefile                    # Cibles make
└── .env.example                # Variables d'environnement de référence
>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
```

---

## Prérequis

- Docker ≥ 24
- Docker Compose ≥ 2.20
- Make (GNU)
- Un répertoire local contenant des sous-dossiers de projets Compose

---

## Démarrage rapide

```bash
# 1. Cloner le dépôt
git clone https://github.com/chrysa/container-webview.git
cd container-webview

# 2. Copier et adapter la configuration
cp .env.example .env
# Éditer .env : SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, PROJECTS_PATH

# 3. Créer un répertoire de projets (ou pointer vers le vôtre)
mkdir -p data/projects

# 4. Lancer le stack de développement
docker compose up --build

# 5. Accéder à l'interface
#   Frontend : http://localhost:3000
#   API docs : http://localhost:8000/docs
```

Identifiants par défaut si non configurés : `admin` / `admin`.

---

## Configuration

Toutes les variables sont documentées dans [.env.example](.env.example).

| Variable | Défaut | Description |
|---|---|---|
| `SECRET_KEY` | `change-me-in-production` | Clé de signature JWT — **à changer en production** |
| `ADMIN_USERNAME` | `admin` | Identifiant admin local |
| `ADMIN_PASSWORD` | `admin` | Mot de passe admin local — **à changer en production** |
| `PROJECTS_PATH` | `/projects` | Chemin dans le conteneur vers les projets Compose |
| `LDAP_SERVER` | _(vide)_ | URL LDAP (`ldap://host:389`) — vide = désactivé |
| `LDAP_BASE_DN` | _(vide)_ | Base DN LDAP |
| `FRONTEND_PORT` | `3000` | Port exposé pour le frontend |
| `VITE_API_URL` | `http://localhost:8000` | URL de l'API vue depuis le navigateur |

Le volume `${PROJECTS_PATH:-./data/projects}:/projects:ro` dans `docker-compose.yml` monte votre répertoire local de projets Compose.

---

## Endpoints API

Documentation interactive disponible sur `http://localhost:8000/docs` (Swagger UI).

| Méthode | Chemin | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Authentification — retourne un JWT Bearer |
| `GET` | `/api/auth/check` | Valide le token courant |
| `GET` | `/api/projects` | Liste tous les projets Compose détectés |
| `GET` | `/api/projects/{id}` | Détail d'un projet |
| `GET` | `/api/projects/{id}/topology` | Graphe de topologie du projet |
| `GET` | `/api/projects/{id}/metrics` | Métriques CPU/RAM/réseau de tous les conteneurs |
| `POST` | `/api/projects/{id}/services/{svc}/start` | Démarrer un service |
| `POST` | `/api/projects/{id}/services/{svc}/stop` | Arrêter un service |
| `POST` | `/api/projects/{id}/services/{svc}/restart` | Redémarrer un service |
| `POST` | `/api/projects/{id}/services/{svc}/pause` | Mettre en pause |
| `POST` | `/api/projects/{id}/services/{svc}/unpause` | Reprendre depuis la pause |
| `GET` | `/api/alerts` | Toutes les alertes actives |
| `GET` | `/api/alerts/project/{id}` | Alertes filtrées par projet |
| `WS` | `/api/projects/{id}/services/{svc}/logs` | Logs en streaming (WebSocket) |

---

## Commandes Make

```
make docker-build           # Rebuild les images sans cache
make docker-up              # Lance le stack (foreground)
make docker-up-detach       # Lance le stack en arrière-plan
make docker-stop            # Arrête les services

make api-tests              # Lance les tests backend
make api-tests-cov          # Tests + rapport de couverture terminal
make api-tests-html         # Tests + rapport HTML (htmlcov/)
make api-lint               # Ruff linter
make api-format             # Ruff formatter
make api-typecheck          # mypy

make pre-commit             # Lance tous les hooks pre-commit
make ci-run-local           # Lance le pipeline CI localement
```

---

## Tests

Les tests backend utilisent **pytest** avec couverture ≥ 80 %.

```bash
# Lancer tous les tests (Docker)
make api-tests

# Avec rapport de couverture
make api-tests-cov

# Avec rapport HTML
make api-tests-html
```

Structure des tests :

```
api/app/tests/
├── conftest.py                  # Fixtures partagées (fake, api_client, auth_headers…)
├── test_main.py                 # Endpoint /api (ping)
├── services/
│   ├── test_docker_client.py
│   ├── test_lifecycle_service.py
│   ├── test_alerts_service.py
│   ├── test_metrics_service.py
│   ├── test_project_manager.py
│   ├── test_auth_service.py
│   └── test_topology_service.py
└── routers/
    ├── test_auth.py
    ├── test_projects.py
    ├── test_lifecycle.py
    ├── test_metrics.py
    ├── test_alerts.py
    └── test_topology.py
```

---

## Roadmap

- [ ] Gestion dynamique des projets depuis le graphe
- [ ] Création/modification de services via l'interface
- [ ] Export du docker-compose (global, par service, dev/prod)
- [ ] Accès aux logs depuis l'interface (WebSocket)
- [ ] Notifications navigateur sur changement d'état des conteneurs
- [ ] Authentification multi-utilisateurs
- [ ] Extension Docker Desktop
