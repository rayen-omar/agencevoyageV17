# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class TestPaiement(TransactionCase):
    """Tests pour le modèle Paiement"""

    def setUp(self):
        super(TestPaiement, self).setUp()
        
        # Créer un client
        self.client = self.env['agencevoyage.client'].create({
            'nom': 'Test',
            'prenom': 'Client',
            'email': 'client@test.com',
            'telephone': '0123456789',
            'adresse': '123 Rue Test',
            'nationalite': 'Française',
            'sexe': 'masculin',
        })
        
        # Créer une destination et un voyage
        destination = self.env['agencevoyage.destination'].create({
            'nom_lieu': 'Paris',
            'ville': 'Paris',
            'pays': 'France',
            'adresse': 'Paris, France',
        })
        
        self.voyage = self.env['agencevoyage.voyage'].create({
            'titre_voyage': 'Voyage Test',
            'destination_id': destination.id,
            'ville_depart': 'Lyon',
            'date_debut': date.today() + timedelta(days=30),
            'date_fin': date.today() + timedelta(days=37),
            'prix_adulte': 500.0,
            'prix_enfant': 300.0,
            'place_total': 20,
        })
        
        # Créer une réservation
        self.reservation = self.env['agencevoyage.reservation'].create({
            'date_reservation': date.today(),
            'voyage_id': self.voyage.id,
            'client_id': self.client.id,
            'montant_total': 1000.0,
        })

    def test_create_paiement(self):
        """Test de création d'un paiement"""
        paiement = self.env['agencevoyage.paiement'].create({
            'reservation_id': self.reservation.id,
            'client_id': self.client.id,
            'type_paiement': 'encaissement',
            'montant': 500.0,
            'date_paiement': date.today(),
            'mode_paiement': 'especes',
        })
        self.assertTrue(paiement.name)
        self.assertEqual(paiement.statut, 'en_attente')

    def test_validation_montant_positif(self):
        """Test que le montant doit être positif"""
        with self.assertRaises(ValidationError):
            self.env['agencevoyage.paiement'].create({
                'reservation_id': self.reservation.id,
                'client_id': self.client.id,
                'type_paiement': 'encaissement',
                'montant': -100.0,
                'date_paiement': date.today(),
                'mode_paiement': 'especes',
            })

    def test_validation_montant_coherence(self):
        """Test que le montant ne dépasse pas le reste à payer"""
        # Le reste à payer est 1000.0
        # Essayer de payer 1500.0
        with self.assertRaises(ValidationError):
            self.env['agencevoyage.paiement'].create({
                'reservation_id': self.reservation.id,
                'client_id': self.client.id,
                'type_paiement': 'encaissement',
                'montant': 1500.0,
                'date_paiement': date.today(),
                'mode_paiement': 'especes',
                'statut': 'paye',
            })

    def test_generation_caisse_automatique(self):
        """Test que la création d'un paiement payé génère une opération de caisse"""
        paiement = self.env['agencevoyage.paiement'].create({
            'reservation_id': self.reservation.id,
            'client_id': self.client.id,
            'type_paiement': 'encaissement',
            'montant': 500.0,
            'date_paiement': date.today(),
            'mode_paiement': 'especes',
            'statut': 'paye',
        })
        
        # Vérifier qu'une opération de caisse a été créée
        caisse_ops = self.env['agencevoyage.caisse'].search([
            ('paiement_client_id', '=', paiement.id)
        ])
        self.assertEqual(len(caisse_ops), 1)
        self.assertEqual(caisse_ops.montant, 500.0)

