# Guide Utilisateur - Agence Voyage

## Table des matières

1. [Introduction](#introduction)
2. [Premiers pas](#premiers-pas)
3. [Gestion des clients](#gestion-des-clients)
4. [Gestion des voyages](#gestion-des-voyages)
5. [Gestion des réservations](#gestion-des-réservations)
6. [Gestion des paiements](#gestion-des-paiements)
7. [Gestion de la caisse](#gestion-de-la-caisse)
8. [Tableau de bord](#tableau-de-bord)
9. [Rapports et exports](#rapports-et-exports)

---

## Introduction

Le module **Agence Voyage** est une application complète de gestion pour agences de voyage. Il permet de gérer les clients, les voyages, les réservations, les paiements et la caisse de manière centralisée et automatisée.

### Fonctionnalités principales

- ✅ Gestion complète des clients
- ✅ Création et gestion des voyages
- ✅ Réservations avec calcul automatique des prix
- ✅ Gestion des paiements clients et fournisseurs
- ✅ Journal de caisse avec calcul automatique des soldes
- ✅ Tableau de bord avec statistiques
- ✅ Rapports PDF professionnels
- ✅ Exports Excel et CSV
- ✅ Notifications emails automatiques

---

## Premiers pas

### Accès au module

1. Connectez-vous à Odoo
2. Dans le menu principal, cliquez sur **"Agence Voyage"**
3. Vous verrez le menu principal avec toutes les sections

### Tableau de bord

Le **Tableau de Bord** est votre point d'entrée principal. Il affiche :
- Statistiques des réservations
- État de la caisse
- Bénéfices du mois
- Actions rapides

---

## Gestion des clients

### Créer un client

1. Menu **Agence Voyage** → **Clients**
2. Cliquez sur **"Créer"**
3. Remplissez les informations :
   - **Prénom** et **Nom** (obligatoires)
   - **Email** (pour les notifications)
   - **Téléphone** (obligatoire)
   - **Adresse** (obligatoire)
   - **Nationalité** (obligatoire)
   - **Photo** (optionnel)
   - **Numéro CIN** ou **Passeport** (optionnel)

4. Cliquez sur **"Enregistrer"**

### Vues disponibles

- **Kanban** : Vue en cartes avec photos
- **Liste** : Vue tableau classique
- **Formulaire** : Vue détaillée

---

## Gestion des voyages

### Créer un voyage

1. Menu **Agence Voyage** → **Voyages**
2. Cliquez sur **"Créer"**
3. Remplissez les informations de base :
   - **Titre du voyage** (obligatoire)
   - **Destination** (obligatoire)
   - **Ville de départ** (obligatoire)
   - **Date de début** et **Date de fin** (obligatoires)
   - **Prix adulte** et **Prix enfant** (obligatoires)
   - **Places totales** (obligatoire)
   - **Photo** (optionnel)

4. Configurez les détails dans les onglets :
   - **Programme jour par jour** : Programme détaillé
   - **Transports** : Moyens de transport
   - **Hôtels** : Hôtels inclus
   - **Restauration** : Repas inclus
   - **Guides** : Guides disponibles
   - **Équipements** : Équipements fournis

5. Cliquez sur **"Enregistrer"**

### Vues disponibles

- **Kanban** : Vue en cartes groupées par statut (Planifié, En cours, Terminé)
- **Calendrier** : Vue calendrier avec dates de début/fin
- **Liste** : Vue tableau
- **Formulaire** : Vue détaillée

### Calcul automatique

- **Places réservées** : Calculé automatiquement à partir des réservations confirmées
- **Places disponibles** : Calculé automatiquement (Total - Réservées)
- **Statut du voyage** : Calculé automatiquement selon les dates (Planifié, En cours, Terminé)

---

## Gestion des réservations

### Créer une réservation

1. Menu **Agence Voyage** → **Réservations**
2. Cliquez sur **"Créer"**
3. Remplissez les informations :
   - **Date de réservation** (obligatoire)
   - **Voyage** (obligatoire)
   - **Client** (obligatoire)
   - **Statut** : Par défaut "En attente"

4. Ajoutez les voyageurs dans l'onglet **"Voyageurs"** :
   - Cliquez sur **"Ajouter une ligne"**
   - Remplissez : Nom, Type (Adulte/Enfant), Âge
   - Le nombre d'adultes et d'enfants est calculé automatiquement

5. Configurez les chambres dans l'onglet **"Chambres"** (optionnel)

6. Vérifiez les prix dans l'onglet **"Calcul des prix"** :
   - **Prix Transport** : Calculé automatiquement (Prix adulte × Adultes + Prix enfant × Enfants)
   - **Prix Hôtel** : Basé sur les chambres réservées
   - **Prix Restauration** : Basé sur les repas du voyage
   - **Prix Guide** : Basé sur les guides du voyage
   - **Prix Équipement** : Basé sur les équipements du voyage
   - **Total** : Somme de tous les prix

7. Cliquez sur **"Enregistrer"**

### Confirmer une réservation

1. Ouvrez la réservation
2. Vérifiez que des voyageurs sont ajoutés
3. Cliquez sur **"Confirmer la Réservation"**
4. Un email de confirmation sera envoyé automatiquement au client (si email renseigné)
5. Les places du voyage seront mises à jour automatiquement

**⚠️ Important** : La confirmation vérifie automatiquement :
- Qu'il y a au moins un voyageur
- Que les places sont disponibles
- Que la date de réservation est avant le début du voyage

### Annuler une réservation

1. Ouvrez la réservation
2. Cliquez sur **"Annuler la Réservation"**
3. Un email de notification sera envoyé au client

### Envoyer un rappel de paiement

1. Ouvrez une réservation avec un reste à payer
2. Vérifiez que le client a un email renseigné
3. Cliquez sur **"Envoyer Rappel Paiement"**
4. Un email sera envoyé au client avec le détail du reste à payer

### Vues disponibles

- **Liste** : Vue tableau avec totaux
- **Formulaire** : Vue détaillée avec onglets
- **Graphique** : Graphique en barres des ventes par mois
- **Pivot** : Tableau croisé dynamique pour analyse

---

## Gestion des paiements

### Créer un paiement client (Encaissement)

1. Menu **Agence Voyage** → **Paiements**
2. Cliquez sur **"Créer"**
3. Remplissez les informations :
   - **Type de paiement** : Sélectionnez "Encaissement (Client)"
   - **Client** (obligatoire)
   - **Réservation** (optionnel, pour lier à une réservation)
   - **Date de paiement** (obligatoire)
   - **Montant** (obligatoire, doit être positif)
   - **Mode de paiement** (obligatoire)
   - **Référence bancaire** (optionnel)
   - **Statut** : Par défaut "En attente"

4. Cliquez sur **"Enregistrer"**

5. Pour valider le paiement, changez le statut à **"Payé"**
   - Une opération de caisse sera créée automatiquement

### Créer un paiement fournisseur (Décaissement)

1. Même procédure, mais sélectionnez **"Décaissement (Fournisseur)"**
2. Remplissez le **Fournisseur** et éventuellement l'**Achat**

### Imprimer un reçu

1. Ouvrez un paiement avec le statut **"Payé"**
2. Cliquez sur **"Imprimer Reçu"**
3. Un PDF sera généré avec tous les détails

### Vues disponibles

- **Liste** : Vue tableau
- **Formulaire** : Vue détaillée
- **Graphique** : Graphique linéaire des paiements par mois
- **Pivot** : Analyse par type, statut et date

---

## Gestion de la caisse

### Créer une opération de caisse

Les opérations de caisse sont créées automatiquement lors de la validation d'un paiement. Vous pouvez aussi en créer manuellement :

1. Menu **Agence Voyage** → **Caisse**
2. Cliquez sur **"Créer"**
3. Remplissez les informations :
   - **Date d'opération** (obligatoire)
   - **Type d'opération** : Encaissement ou Décaissement
   - **Paiement** : Lier à un paiement existant (optionnel)
   - **Montant** (obligatoire, doit être positif)
   - **Mode de paiement** (obligatoire)
   - **Description** (optionnel)
   - **Statut** : Par défaut "Validé"

4. Cliquez sur **"Enregistrer"**

### Soldes automatiques

Les soldes sont calculés automatiquement :
- **Solde avant** : Solde avant cette opération
- **Solde après** : Solde après cette opération
- **Solde actuel** : Solde total actuel de la caisse (affiché en haut du formulaire)

### Annuler une opération

1. Ouvrez l'opération de caisse
2. Cliquez sur **"Annuler l'opération"**
3. Le statut passera à "Annulé" et les soldes seront recalculés

### Vues disponibles

- **Liste** : Vue tableau avec totaux
- **Formulaire** : Vue détaillée avec soldes
- **Graphique** : Graphique linéaire de l'évolution des montants
- **Pivot** : Analyse par type, statut et date

---

## Tableau de bord

### Accéder au tableau de bord

Menu **Agence Voyage** → **Tableau de Bord**

### Statistiques affichées

#### Réservations
- **Total Réservations** : Nombre total de réservations
- **Réservations Confirmées** : Nombre de réservations confirmées
- **CA Réservations** : Chiffre d'affaires des réservations confirmées
- **Reste à Payer Total** : Montant total restant à payer

#### Caisse
- **Solde Actuel** : Solde total actuel de la caisse
- **Encaissements (Mois)** : Total des encaissements du mois en cours
- **Décaissements (Mois)** : Total des décaissements du mois en cours
- **Bénéfice (Mois)** : Bénéfice du mois (Encaissements - Décaissements)

### Actions rapides

- **Voir Réservations** : Ouvre la liste des réservations
- **Voir Caisse** : Ouvre la liste de la caisse
- **Voir Paiements** : Ouvre la liste des paiements
- **Actualiser** : Rafraîchit les statistiques

---

## Rapports et exports

### Rapports PDF

#### Rapport Réservation

1. Ouvrez une réservation
2. Cliquez sur **"Imprimer"** (menu en haut à droite)
3. Sélectionnez **"Rapport Réservation"**
4. Le PDF contient :
   - Détails de la réservation
   - Liste des voyageurs
   - Détail des prix
   - Reste à payer

#### Rapport Caisse

1. Ouvrez une opération de caisse
2. Cliquez sur **"Imprimer"**
3. Sélectionnez **"Journal de Caisse"**
4. Le PDF contient tous les détails de l'opération

#### Reçu de Paiement

1. Ouvrez un paiement avec statut "Payé"
2. Cliquez sur **"Imprimer Reçu"**
3. Un reçu professionnel sera généré

### Exports Excel/CSV

#### Exporter les réservations

1. Menu **Agence Voyage** → **Réservations**
2. Sélectionnez les réservations à exporter (ou laissez vide pour tout exporter)
3. Menu **Action** → **"Exporter en Excel"** ou **"Exporter en CSV"**
4. Le fichier sera téléchargé automatiquement

#### Exporter la caisse

1. Menu **Agence Voyage** → **Caisse**
2. Même procédure que pour les réservations

**Note** : Pour les exports Excel, le module `xlsxwriter` doit être installé :
```bash
pip install xlsxwriter
```

---

## Conseils et bonnes pratiques

### Gestion des réservations

- ✅ Toujours vérifier les places disponibles avant de confirmer
- ✅ Ajouter les voyageurs avant de confirmer
- ✅ Vérifier les prix calculés automatiquement
- ✅ Utiliser le bouton "Envoyer Rappel Paiement" pour les clients en retard

### Gestion de la caisse

- ✅ Vérifier régulièrement le solde actuel
- ✅ Utiliser les vues graphiques pour analyser les tendances
- ✅ Annuler les opérations erronées plutôt que de les supprimer

### Notifications emails

- ✅ S'assurer que les clients ont un email valide
- ✅ Les emails sont envoyés automatiquement lors des confirmations/annulations
- ✅ Utiliser le bouton "Envoyer Rappel Paiement" pour les rappels manuels

### Statistiques

- ✅ Consulter régulièrement le Tableau de Bord
- ✅ Utiliser les vues Graphique et Pivot pour des analyses approfondies
- ✅ Exporter les données pour des analyses externes

---

## Support

Pour toute question ou problème :
- Consultez la documentation technique
- Contactez l'administrateur système
- Vérifiez les logs Odoo en cas d'erreur

---

**Version** : 17.0.1.0.0  
**Dernière mise à jour** : 2026

