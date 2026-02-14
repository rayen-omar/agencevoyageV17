# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class TestVoyage(TransactionCase):
    """Tests pour le modèle Voyage"""

    def setUp(self):
        super(TestVoyage, self).setUp()
        
        # Créer une destination
        self.destination = self.env['agencevoyage.destination'].create({
            'nom_lieu': 'Paris',
            'ville': 'Paris',
            'pays': 'France',
            'adresse': 'Paris, France',
        })

    def test_create_voyage(self):
        """Test de création d'un voyage"""
        voyage = self.env['agencevoyage.voyage'].create({
            'titre_voyage': 'Voyage Test',
            'destination_id': self.destination.id,
            'ville_depart': 'Lyon',
            'date_debut': date.today() + timedelta(days=30),
            'date_fin': date.today() + timedelta(days=37),
            'prix_adulte': 500.0,
            'prix_enfant': 300.0,
            'place_total': 20,
        })
        self.assertEqual(voyage.titre_voyage, 'Voyage Test')
        self.assertEqual(voyage.place_total, 20)

    def test_validation_dates(self):
        """Test que la date de fin doit être après la date de début"""
        with self.assertRaises(ValidationError):
            self.env['agencevoyage.voyage'].create({
                'titre_voyage': 'Voyage Test',
                'destination_id': self.destination.id,
                'ville_depart': 'Lyon',
                'date_debut': date.today() + timedelta(days=30),
                'date_fin': date.today() + timedelta(days=20),  # Avant la date de début
                'prix_adulte': 500.0,
                'prix_enfant': 300.0,
                'place_total': 20,
            })

    def test_calcul_places_reservees(self):
        """Test du calcul automatique des places réservées"""
        voyage = self.env['agencevoyage.voyage'].create({
            'titre_voyage': 'Voyage Test',
            'destination_id': self.destination.id,
            'ville_depart': 'Lyon',
            'date_debut': date.today() + timedelta(days=30),
            'date_fin': date.today() + timedelta(days=37),
            'prix_adulte': 500.0,
            'prix_enfant': 300.0,
            'place_total': 20,
        })
        
        # Créer un client
        client = self.env['agencevoyage.client'].create({
            'nom': 'Test',
            'prenom': 'Client',
            'email': 'test@test.com',
            'telephone': '0123456789',
            'adresse': '123 Rue Test',
            'nationalite': 'Française',
            'sexe': 'masculin',
        })
        
        # Créer une réservation confirmée avec 5 personnes
        reservation = self.env['agencevoyage.reservation'].create({
            'date_reservation': date.today(),
            'voyage_id': voyage.id,
            'client_id': client.id,
            'statut': 'confirmee',
        })
        
        # Ajouter 5 voyageurs
        for i in range(5):
            self.env['agencevoyage.voyageur'].create({
                'reservation_id': reservation.id,
                'nom': f'Voyageur {i}',
                'type_voyageur': 'adulte',
                'age': 30,
            })
        
        voyage._compute_place_reserve()
        self.assertEqual(voyage.place_reserve, 5)
        self.assertEqual(voyage.place_disponible, 15)

