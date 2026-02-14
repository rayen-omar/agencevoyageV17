# Module Agence Voyage - Gestion des Clients

## Description
Module Odoo 17 pour la gestion des clients d'une agence de voyage.

## Fonctionnalités

### Modèle Client
Le module permet de gérer les informations suivantes pour chaque client :

- **Informations personnelles** :
  - Prénom
  - Nom
  - Nom complet (calculé automatiquement)
  - Sexe (Masculin/Féminin)
  - Nationalité
  - Photo

- **Coordonnées** :
  - Email
  - Téléphone
  - Adresse complète

### Vues disponibles
- **Vue Formulaire** : Interface claire avec photo, informations personnelles et coordonnées
- **Vue Liste** : Affichage tabulaire des clients
- **Vue Kanban** : Cartes visuelles avec photo et informations principales
- **Vue Recherche** : Filtres par sexe, nationalité et recherche par nom

### Fonctionnalités supplémentaires
- Suivi des modifications (Chatter)
- Validation automatique de l'email
- Calcul automatique du nom complet
- Widgets adaptés (email, téléphone, image)

## Installation

1. Copier le module dans le dossier `custom_addons`
2. Redémarrer le serveur Odoo
3. Activer le mode développeur
4. Aller dans Apps > Mettre à jour la liste des applications
5. Rechercher "Agence Voyage" et installer

## Utilisation

Après installation, un nouveau menu "Agence Voyage" apparaît dans la barre de navigation principale.
Cliquez sur "Clients" pour accéder à la gestion des clients.

## Auteur
Agence Voyage

## Licence
LGPL-3
