# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta


class TestReservation(TransactionCase):
    """Tests pour le modèle Reservation"""

    def setUp(self):
        super(TestReservation, self).setUp()
        
        # Créer un client de test
        self.client = self.env['agencevoyage.client'].create({
            'nom': 'Dupont',
            'prenom': 'Jean',
            'email': 'jean.dupont@test.com',
            'telephone': '0123456789',
            'adresse': '123 Rue Test',
            'nationalite': 'Française',
            'sexe': 'masculin',
        })
        
        # Créer une destination
        self.destination = self.env['agencevoyage.destination'].create({
            'nom_lieu': 'Paris',
            'ville': 'Paris',
            'pays': 'France',
            'adresse': 'Paris, France',
        })
        
        # Créer un voyage
        self.voyage = self.env['agencevoyage.voyage'].create({
            'titre_voyage': 'Voyage Test Paris',
            'destination_id': self.destination.id,
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
            'statut': 'en_attente',
        })

    def test_create_reservation(self):
        """Test de création d'une réservation"""
        reservation = self.env['agencevoyage.reservation'].create({
            'date_reservation': date.today(),
            'voyage_id': self.voyage.id,
            'client_id': self.client.id,
        })
        self.assertTrue(reservation.name)
        self.assertEqual(reservation.statut, 'en_attente')

    def test_confirmer_reservation(self):
        """Test de confirmation d'une réservation"""
        # Ajouter un voyageur
        self.env['agencevoyage.voyageur'].create({
            'reservation_id': self.reservation.id,
            'nom': 'Test Voyageur',
            'type_voyageur': 'adulte',
            'age': 30,
        })
        
        # Confirmer la réservation
        self.reservation.action_confirmer()
        self.assertEqual(self.reservation.statut, 'confirmee')

    def test_confirmer_reservation_sans_voyageur(self):
        """Test que la confirmation échoue sans voyageur"""
        with self.assertRaises(UserError):
            self.reservation.action_confirmer()

    def test_annuler_reservation(self):
        """Test d'annulation d'une réservation"""
        self.reservation.action_annuler()
        self.assertEqual(self.reservation.statut, 'annulee')

    def test_validation_places_disponibles(self):
        """Test de validation des places disponibles"""
        # Créer une autre réservation confirmée qui prend toutes les places
        autre_reservation = self.env['agencevoyage.reservation'].create({
            'date_reservation': date.today(),
            'voyage_id': self.voyage.id,
            'client_id': self.client.id,
            'statut': 'confirmee',
        })
        
        # Ajouter 20 voyageurs (toutes les places)
        for i in range(20):
            self.env['agencevoyage.voyageur'].create({
                'reservation_id': autre_reservation.id,
                'nom': f'Voyageur {i}',
                'type_voyageur': 'adulte',
                'age': 30,
            })
        
        # Ajouter un voyageur à notre réservation
        self.env['agencevoyage.voyageur'].create({
            'reservation_id': self.reservation.id,
            'nom': 'Test',
            'type_voyageur': 'adulte',
            'age': 30,
        })
        
        # La confirmation doit échouer car plus de places
        with self.assertRaises(UserError):
            self.reservation.action_confirmer()

    def test_validation_date_reservation(self):
        """Test de validation de la date de réservation"""
        # Créer une réservation avec une date après le début du voyage
        reservation = self.env['agencevoyage.reservation'].create({
            'date_reservation': self.voyage.date_debut + timedelta(days=1),
            'voyage_id': self.voyage.id,
            'client_id': self.client.id,
        })
        
        # La validation doit échouer
        with self.assertRaises(ValidationError):
            reservation._check_date_reservation()

    def test_calcul_prix_total(self):
        """Test du calcul automatique du prix total"""
        # Ajouter des voyageurs
        self.env['agencevoyage.voyageur'].create({
            'reservation_id': self.reservation.id,
            'nom': 'Adulte 1',
            'type_voyageur': 'adulte',
            'age': 30,
        })
        self.env['agencevoyage.voyageur'].create({
            'reservation_id': self.reservation.id,
            'nom': 'Enfant 1',
            'type_voyageur': 'enfant',
            'age': 10,
        })
        
        # Le prix transport doit être calculé
        self.reservation._compute_prix_total()
        prix_attendu = 500.0 + 300.0  # 1 adulte + 1 enfant
        self.assertEqual(self.reservation.prix_transport, prix_attendu)

    def test_calcul_reste_a_payer(self):
        """Test du calcul du reste à payer"""
        # Définir un montant total
        self.reservation.montant_total = 1000.0
        
        # Créer un paiement payé
        paiement = self.env['agencevoyage.paiement'].create({
            'reservation_id': self.reservation.id,
            'client_id': self.client.id,
            'type_paiement': 'encaissement',
            'montant': 300.0,
            'statut': 'paye',
            'date_paiement': date.today(),
            'mode_paiement': 'especes',
        })
        
        self.reservation._compute_reste_a_payer()
        self.assertEqual(self.reservation.deja_paye, 300.0)
        self.assertEqual(self.reservation.reste_a_payer, 700.0)

