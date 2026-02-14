# Tests Unitaires - Agence Voyage

## Structure des tests

Les tests unitaires sont organisés par modèle :

- `test_reservation.py` : Tests pour le modèle Reservation
- `test_caisse.py` : Tests pour le modèle Caisse
- `test_paiement.py` : Tests pour le modèle Paiement
- `test_voyage.py` : Tests pour le modèle Voyage

## Exécution des tests

### Méthode 1 : Via la ligne de commande Odoo

```bash
# Exécuter tous les tests du module
odoo-bin -c odoo.conf --test-enable --stop-after-init -d nom_base_de_donnees --log-level=test

# Exécuter un test spécifique
odoo-bin -c odoo.conf --test-enable --stop-after-init -d nom_base_de_donnees --log-level=test --test-tags=agencevoyage.tests.test_reservation
```

### Méthode 2 : Via l'interface Odoo (Mode Développeur)

1. Activer le mode développeur
2. Aller dans **Paramètres** → **Technique** → **Tests** → **Tests unitaires**
3. Sélectionner le module "agencevoyage"
4. Cliquer sur **Exécuter les tests**

## Tests disponibles

### TestReservation

- ✅ `test_create_reservation` : Création d'une réservation
- ✅ `test_confirmer_reservation` : Confirmation d'une réservation
- ✅ `test_confirmer_reservation_sans_voyageur` : Échec si pas de voyageur
- ✅ `test_annuler_reservation` : Annulation d'une réservation
- ✅ `test_validation_places_disponibles` : Validation des places disponibles
- ✅ `test_validation_date_reservation` : Validation de la date de réservation
- ✅ `test_calcul_prix_total` : Calcul automatique du prix total
- ✅ `test_calcul_reste_a_payer` : Calcul du reste à payer

### TestCaisse

- ✅ `test_create_encaissement` : Création d'un encaissement
- ✅ `test_validation_montant_positif` : Validation montant positif
- ✅ `test_calcul_solde` : Calcul des soldes (avant/après)
- ✅ `test_action_annuler` : Annulation d'une opération

### TestPaiement

- ✅ `test_create_paiement` : Création d'un paiement
- ✅ `test_validation_montant_positif` : Validation montant positif
- ✅ `test_validation_montant_coherence` : Validation cohérence avec reste à payer
- ✅ `test_generation_caisse_automatique` : Génération automatique d'opération de caisse

### TestVoyage

- ✅ `test_create_voyage` : Création d'un voyage
- ✅ `test_validation_dates` : Validation des dates (fin > début)
- ✅ `test_calcul_places_reservees` : Calcul automatique des places réservées

## Notes importantes

- Les tests utilisent `TransactionCase` qui crée une transaction par test
- Chaque test crée ses propres données de test dans `setUp()`
- Les tests vérifient les validations, calculs automatiques et workflows
- Les tests sont isolés et ne dépendent pas les uns des autres

## Ajout de nouveaux tests

Pour ajouter un nouveau test :

1. Créer un fichier `test_nom_modele.py` dans le dossier `tests/`
2. Importer `TransactionCase` depuis `odoo.tests.common`
3. Créer une classe héritant de `TransactionCase`
4. Définir `setUp()` pour créer les données de test
5. Créer des méthodes `test_*` pour chaque cas de test
6. Importer le fichier dans `tests/__init__.py`

Exemple :

```python
# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestMonModele(TransactionCase):
    """Tests pour le modèle MonModele"""
    
    def setUp(self):
        super(TestMonModele, self).setUp()
        # Créer les données de test
    
    def test_mon_cas(self):
        """Description du test"""
        # Code du test
        pass
```

