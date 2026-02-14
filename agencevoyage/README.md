# Module Agence Voyage - Odoo 17

## Description

Module complet de gestion pour agences de voyage permettant de gérer les clients, voyages, réservations, paiements et caisse de manière centralisée et automatisée.

## Fonctionnalités principales

### Gestion des clients
- Informations personnelles complètes (nom, prénom, email, téléphone, adresse)
- Photo du client
- Documents d'identité (CIN, Passeport)
- Vue Kanban et Liste
- Validations (email, téléphone)

### Gestion des voyages
- Création de voyages avec destinations
- Programme jour par jour
- Gestion des transports, hôtels, restauration, guides, équipements
- Calcul automatique des places réservées/disponibles
- Vue Kanban (groupée par statut), Calendrier, Liste
- Statut automatique (Planifié, En cours, Terminé)

### Gestion des réservations
- Création de réservations avec calcul automatique des prix
- Gestion des voyageurs (adultes/enfants)
- Gestion des chambres
- Calcul automatique : Transport, Hôtel, Restauration, Guide, Équipement
- Workflow : En attente → Confirmée → Terminée
- Validations : Places disponibles, Date de réservation
- Boutons : Confirmer, Annuler, Envoyer Rappel Paiement
- Calcul automatique : Déjà payé, Reste à payer
- Vues : Liste, Formulaire, Graphique, Pivot

### Gestion des paiements
- Paiements clients (Encaissements)
- Paiements fournisseurs (Décaissements)
- Génération automatique d'opérations de caisse
- Validations : Montant positif, Cohérence avec reste à payer
- Impression de reçus PDF
- Vues : Liste, Formulaire, Graphique, Pivot

### Gestion de la caisse
- Journal de caisse complet
- Calcul automatique des soldes (avant/après/actuel)
- Encaissements et décaissements
- Validations : Montant positif, Cohérence
- Workflow : En attente → Validé → Annulé
- Vues : Liste, Formulaire, Graphique, Pivot

### Tableau de bord
- Statistiques des réservations (Total, Confirmées, CA, Reste à payer)
- Statistiques de la caisse (Solde actuel, Encaissements/Décaissements du mois, Bénéfice)
- Actions rapides vers les principales vues
- Actualisation en temps réel

### Rapports PDF
- Rapport Réservation (détails complets)
- Rapport Caisse (journal de caisse)
- Reçu de Paiement (format professionnel)

### Exports de données
- Export Excel (Réservations, Caisse)
- Export CSV (Réservations, Caisse)
- Actions disponibles dans les menus

### Notifications emails
- Email de confirmation de réservation (automatique)
- Email de rappel de paiement (manuel)
- Email de changement de statut (automatique)

### Statistiques et analyses
- Vues graphiques (barres, lignes) pour Réservations, Caisse, Achat, Paiement
- Vues pivot pour analyses croisées
- Filtres et regroupements avancés

## Installation

1. Copier le module dans `custom_addons/agencevoyage`
2. Mettre à jour la liste des applications dans Odoo
3. Installer le module "Agence Voyage"

## Dépendances

- `base` : Module de base Odoo
- `web` : Interface web
- `mail` : Système de messagerie et notifications

## Dépendances optionnelles

Pour les exports Excel :
```bash
pip install xlsxwriter
```

## Structure du module

```
agencevoyage/
├── __init__.py
├── __manifest__.py
├── README.md
├── data/
│   ├── ir_sequence_data.xml
│   └── email_templates.xml
├── models/
│   ├── __init__.py
│   ├── client.py
│   ├── destination.py
│   ├── voyage.py
│   ├── reservation.py
│   ├── paiement.py
│   ├── caisse.py
│   ├── achat.py
│   └── ... (autres modèles)
├── views/
│   ├── client_views.xml
│   ├── voyage_views.xml
│   ├── reservation_views.xml
│   ├── paiement_views.xml
│   ├── caisse_views.xml
│   └── ... (autres vues)
├── reports/
│   ├── reservation_report.xml
│   ├── caisse_report.xml
│   └── paiement_report.xml
├── report/
│   ├── reservation_template.xml
│   ├── caisse_template.xml
│   └── paiement_template.xml
├── security/
│   └── ir.model.access.csv
├── tests/
│   ├── __init__.py
│   ├── test_reservation.py
│   ├── test_caisse.py
│   ├── test_paiement.py
│   └── test_voyage.py
└── docs/
    └── GUIDE_UTILISATEUR.md
```

## Tests

Les tests unitaires sont disponibles dans le dossier `tests/`. Pour les exécuter :

```bash
odoo-bin -c odoo.conf --test-enable --stop-after-init -d nom_base --log-level=test
```

## Documentation

- **Guide Utilisateur** : `docs/GUIDE_UTILISATEUR.md`
- Documentation technique dans les fichiers Python (docstrings)

## Auteur

Agence Voyage

## Licence

LGPL-3

## Version

17.0.1.0.0
