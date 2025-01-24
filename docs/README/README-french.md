<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/README.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-spanish.md">Español</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-portuguese.md">Português</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-french.md">Français</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-german.md">Deutsch</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-dutch.md">Dutch</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-italian.md">Italiano</a>
</p>

# Django-CRM

*(Logiciel de gestion de la relation client collaboratif et analytique)*

**Django-CRM** est une solution CRM open-source conçue avec deux objectifs principaux :

- **Pour les utilisateurs** : Fournir un logiciel CRM open-source de niveau entreprise avec une suite complète de solutions commerciales.
- **Pour les développeurs** : Simplifier les processus de développement, de personnalisation et de support des serveurs de production.

**Pas besoin d'apprendre un cadre propriétaire**: tout est construit en utilisant le cadre populaire Django.
Le CRM tire également pleinement parti du site d'administration Django, avec une documentation contenue sur une seule page web !

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png" alt="Capture d'écran de Django-CRM" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/deals_screenshot.png)

## Fonctionnalités de gestion de la relation client
|                                   |                                                   |                                            |
|-----------------------------------|---------------------------------------------------|--------------------------------------------|
| ☑️ **Tâches et projets d'équipe** | ☑️ **Gestion des leads**                          | ☑️ **Marketing par email**                 |
| ☑️ **Gestion des contacts**       | ☑️ **Suivi des affaires et prévisions de ventes** | ☑️ **Contrôle d'accès basé sur les rôles** |
| ☑️ **Analyses des ventes**        | ☑️ **Intégration de chat interne**                | ☑️ **Design adapté aux mobiles**           |
| ☑️ **Rapports personnalisables**  | ☑️ **Synchronisation automatique des emails**     | ☑️ **Support multi-devises**               |

En savoir plus sur [les capacités du logiciel](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md).

Django CRM est un logiciel de gestion de la relation client open-source. Ce CRM est écrit en <a href="https://www.python.org" target="_blank"><img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" style="vertical-align: middle" alt="logo python" width="25" height="25"> Python</a>.
Le frontend et le backend sont entièrement basés sur le site d'administration Django [Admin site](https://docs.djangoproject.com/en/dev/ref/contrib/admin/).
L'application CRM utilise des modèles HTML adaptatifs d'administration par défaut.
Django est un cadre extrêmement bien documenté avec de nombreux exemples.
La documentation sur le site d'administration ne prend qu'une seule page web.  
💡 L'**idée originale** est que, puisque l'administration Django est déjà une interface de gestion d'objets professionnelle avec un système de permissions flexible pour les utilisateurs (voir, modifier, ajouter et supprimer des objets), tout ce que vous avez à faire est de créer des modèles pour les objets (tels que Leads, Demandes, Affaires, Entreprises, etc.) et d'ajouter la logique métier.

Tout cela garantit :

- une personnalisation et un développement de projet considérablement plus faciles
- un déploiement de projet et un support de serveur de production plus simples

Le package logiciel fournit deux sites web :

- Site CRM pour tous les utilisateurs
- Site pour les administrateurs

Le **projet est mature et stable**, et a été utilisé avec succès dans des applications réelles pendant de nombreuses années.

## Applications principales

La suite logicielle CRM se compose des **applications principales** suivantes et de leurs modèles :

- **Application de gestion des TÂCHES** :
  (disponible pour tous les utilisateurs par défaut, quel que soit leur rôle)
  - Tâche (avec fichiers associés, chat, rappels, étiquettes - voir [fonctionnalités des tâches](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md))
    - sous-tâches
  - Mémo (mémo de bureau) - voir [fonctionnalités des mémos](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md)
    - tâches / projet
  - Projet (*collection de tâches*):
  - ... (+ *4 autres <a href="https://github.com/DjangoCRM/django-crm/tree/main/tasks/models" target="_blank">modèles</a>*)
- **Application CRM** :
  - Demandes (demandes commerciales)
  - Leads (clients potentiels)
  - Entreprises
  - Personnes de contact (associées à leurs entreprises)
  - Affaires (comme des "Opportunités")
  - Messages électroniques (synchronisation avec les comptes de messagerie des utilisateurs)
  - Produits (biens et services)
  - Paiements (reçus, garantis, haute et basse probabilité)
  - ... (*+ 12 autres <a href="https://github.com/DjangoCRM/django-crm/tree/main/crm/models" target="_blank">modèles</a>*)
[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/income_summary_thumbnail.png" alt="Rapport analytique crm" align="right" width="190px" style="float: right"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)
- **Application ANALYTIQUE** : (aperçu détaillé du logiciel [ici](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_analytics_app_overview.md))
  - Rapport de résumé des revenus (*voir [capture d'écran](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)*)
  - Rapport de l'entonnoir de vente
  - Rapport de résumé des sources de leads
  - ... (+ *5 autres rapports analytiques*)
- **Application de MAILING DE MASSE** :
  - Comptes de messagerie
  - Messages électroniques (newsletters)
  - Signatures électroniques (signatures des utilisateurs)
  - Envois de mails

## Applications de support

Le package CRM contient également des **applications de support** telles que :

- Application de chat (le chat est disponible dans chaque instance de tâche, projet, mémo de bureau et affaire)
- Application VoIP (contacter les clients à partir des affaires)
- Application d'aide (pages d'aide dynamiques en fonction du rôle de l'utilisateur)
- Application commune :
  - 🪪 Profils d'utilisateur
  - ⏰ Rappels (pour les tâches, projets, mémos de bureau et affaires)
  - 📝 Étiquettes (pour les tâches, projets, mémos de bureau et affaires)
  - 📂 Fichiers (pour les tâches, projets, mémos de bureau et affaires)

## Fonctionnalités supplémentaires

- Intégration de formulaires web : Le formulaire de contact CRM a une protection intégrée :
  - reCAPTCHA v3
  - géolocalisation automatique
- Intégration et synchronisation du compte de messagerie de l'utilisateur. Les messages électroniques sont automatiquement :
  - enregistrés dans la base de données CRM
  - liés aux objets CRM appropriés (comme : demandes, leads, affaires, etc.)
- Rappel VoIP vers smartphone
- Envoi de messages via des messageries (comme : Viber, WhatsApp, ...)
- Support Excel : Importer/exporter facilement les détails des contacts.

## Client de messagerie

Le système CRM Python inclut un client de messagerie intégré qui fonctionne en utilisant les protocoles **SMTP** et **IMAP**.
Cela permet à Django-CRM de stocker automatiquement des copies de toute la correspondance liée à chaque demande et affaire dans sa base de données.
La fonctionnalité garantit que même si les communications se produisent via le compte de messagerie externe de l'utilisateur (en dehors du CRM).
Elles sont capturées et organisées dans le système en utilisant un **mécanisme de tickets**.

Le CRM peut s'intégrer avec des fournisseurs de services de messagerie (comme Gmail) qui nécessitent une authentification à deux facteurs obligatoire (en utilisant le protocole **OAuth 2.0**) pour les applications tierces.

## Assistance utilisateur

- Chaque page du CRM inclut un lien vers une page d'aide contextuelle, avec un contenu adapté dynamiquement au rôle de l'utilisateur pour une orientation plus pertinente.
- Des infobulles sont disponibles dans toute l'interface, fournissant des informations instantanées en survolant des éléments tels que des icônes, des boutons, des liens ou des en-têtes de tableau.
- Un [guide utilisateur](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md) complet est également inclus pour une référence et un support approfondis.

## Élevez la productivité de votre équipe avec des solutions CRM collaboratives

Ce CRM est conçu pour améliorer la collaboration au sein des équipes et rationaliser les processus de gestion de projet.
En tant que CRM collaboratif, il permet aux utilisateurs de créer et de gérer des mémos, des tâches et des projets avec facilité.
[Les mémos de bureau](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md) peuvent être dirigés vers les chefs de département ou les cadres de l'entreprise, qui peuvent ensuite transformer ces mémos en tâches ou projets, en assignant des personnes responsables ou des exécutants.
[Les tâches](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md) peuvent être individuelles ou collectives.
Les tâches offrent des fonctionnalités telles que des discussions de chat, des rappels, le partage de fichiers, la création de sous-tâches et le partage de résultats.
Les utilisateurs reçoivent des notifications directement dans le CRM et par email, assurant qu'ils restent informés.
Chaque utilisateur a une vue claire de sa pile de tâches, y compris les priorités, les statuts et les prochaines étapes, améliorant ainsi la productivité et la responsabilité dans la gestion collaborative de la relation client.

## Localisation du projet

Django CRM a un support complet pour la traduction de l'interface, le formatage des dates, des heures et des fuseaux horaires.  
<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/languages.svg" alt="logo django" width="30" height="30" style="vertical-align: middle"> Le logiciel de service client est maintenant disponible en **plusieurs langues**:  
`de, en, es, fr, it, nl, pt-BR, ru, uk`

## Pourquoi choisir Django-CRM ?

- **CRM collaboratif** : Augmentez la productivité de l'équipe avec des outils pour la gestion des tâches, la collaboration sur les projets et la communication interne.
- **CRM analytique** : Obtenez des informations exploitables avec des rapports intégrés tels que l'entonnoir de vente, le résumé des revenus et l'analyse des sources de leads.
- **Basé sur Python et Django** : Aucun cadre propriétaire requis - tout est construit sur Django avec une interface d'administration intuitive.

## Commencer

Si vous trouvez Django-CRM utile, veuillez ⭐️ **étoiler** ce dépôt sur GitHub pour soutenir sa croissance !

Django-CRM peut être facilement déployé comme un projet Django régulier.

📚 Veuillez consulter :

- [Guide d'installation et de configuration](https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide.md)
- [Guide utilisateur](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md)

### Compatibilité

- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/django-logo.svg" alt="logo django" width="30" height="30" style="vertical-align: middle"> Django 5.1.x
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" alt="logo python" width="30" height="30" style="vertical-align: middle"> Python 3.10+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/mysql_logo.svg" alt="logo mysql" width="30" height="30" style="vertical-align: middle"> MySQL 8.0.11+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/postgresql_logo.svg" alt="logo postgresql" width="30" height="30" style="vertical-align: middle"> PostgreSQL 12+

## Contribuer

Les contributions sont les bienvenues ! Il y a de la place pour des améliorations et de nouvelles fonctionnalités.
Consultez notre [Guide de contribution](https://github.com/DjangoCRM/django-crm/blob/main/CONTRIBUTING.md) pour apprendre comment commencer.
Chaque contribution, grande ou petite, fait la différence.

## Licence

Django-CRM est publié sous la licence AGPL-3.0 - consultez le fichier [LICENSE](https://github.com/DjangoCRM/django-crm/blob/main/LICENSE) pour plus de détails.

## Crédits

- Icônes de Google [material](https://fonts.google.com/icons).
- [NicEdit](https://nicedit.com) - Éditeur de contenu WYSIWYG.
