# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date


class TestCaisse(TransactionCase):
    """Tests pour le modèle Caisse"""

    def setUp(self):
        super(TestCaisse, self).setUp()
        
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

    def test_create_encaissement(self):
        """Test de création d'un encaissement"""
        # Créer un nouveau paiement pour ce test
        paiement = self.env['agencevoyage.paiement'].create({
            'client_id': self.client.id,
            'type_paiement': 'encaissement',
            'montant': 500.0,
            'date_paiement': date.today(),
            'mode_paiement': 'especes',
            'statut': 'paye',
        })
        
        caisse = self.env['agencevoyage.caisse'].create({
            'date_operation': date.today(),
            'type_operation': 'encaissement',
            'paiement_client_id': paiement.id,
            'montant': 500.0,
            'mode_paiement': 'especes',
            'statut': 'valide',
        })
        self.assertTrue(caisse.name)
        self.assertEqual(caisse.type_operation, 'encaissement')

    def test_validation_montant_positif(self):
        """Test que le montant doit être positif"""
        # La contrainte @api.constrains lève une ValidationError
        # La contrainte SQL peut aussi lever une exception
        # On teste que la création échoue
        with self.assertRaises(Exception):  # Peut être ValidationError ou exception SQL
            self.env['agencevoyage.caisse'].create({
                'date_operation': date.today(),
                'type_operation': 'encaissement',
                'montant': -100.0,
                'mode_paiement': 'especes',
                'statut': 'valide',
            })

    def test_calcul_solde(self):
        """Test du calcul des soldes"""
        # Calculer le solde initial (avant nos opérations)
        operations_existantes = self.env['agencevoyage.caisse'].search([
            ('statut', '=', 'valide'),
            ('date_operation', '<=', date.today())
        ], order='date_operation asc, id asc')
        
        solde_initial = 0.0
        for op in operations_existantes:
            if op.type_operation == 'encaissement':
                solde_initial += op.montant
            else:
                solde_initial -= op.montant
        
        # Créer plusieurs opérations
        op1 = self.env['agencevoyage.caisse'].create({
            'date_operation': date.today(),
            'type_operation': 'encaissement',
            'montant': 1000.0,
            'mode_paiement': 'especes',
            'statut': 'valide',
        })
        
        op2 = self.env['agencevoyage.caisse'].create({
            'date_operation': date.today(),
            'type_operation': 'decaissement',
            'montant': 300.0,
            'mode_paiement': 'cheque',
            'statut': 'valide',
        })
        
        # Vérifier les soldes
        op1._compute_solde()
        op2._compute_solde()
        
        self.assertEqual(op1.solde_avant, solde_initial)
        self.assertEqual(op1.solde_apres, solde_initial + 1000.0)
        self.assertEqual(op2.solde_avant, solde_initial + 1000.0)
        self.assertEqual(op2.solde_apres, solde_initial + 700.0)

    def test_action_annuler(self):
        """Test d'annulation d'une opération"""
        caisse = self.env['agencevoyage.caisse'].create({
            'date_operation': date.today(),
            'type_operation': 'encaissement',
            'montant': 500.0,
            'mode_paiement': 'especes',
            'statut': 'valide',
        })
        
        caisse.action_annuler()
        self.assertEqual(caisse.statut, 'annule')

