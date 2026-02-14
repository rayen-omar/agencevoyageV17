from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Caisse(models.Model):
    _name = 'agencevoyage.caisse'
    _description = 'Caisse'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'date_operation desc'

    name = fields.Char(
        string='Numéro d\'opération',
        required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('agencevoyage.caisse') or 'Nouveau',
        tracking=True,
        readonly=True
    )
    date_operation = fields.Date(
        string='Date d\'opération',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    type_operation = fields.Selection(
        [
            ('encaissement', 'Encaissement'),
            ('decaissement', 'Décaissement'),
        ],
        string='Type d\'opération',
        required=True,
        default='encaissement',
        tracking=True
    )
    
    # Encaissement
    paiement_client_id = fields.Many2one(
        'agencevoyage.paiement',
        string='Paiement client',
        domain="[('type_paiement', '=', 'encaissement')]",
        tracking=True
    )
    
    # Décaissement
    paiement_fournisseur_id = fields.Many2one(
        'agencevoyage.paiement',
        string='Paiement fournisseur',
        domain="[('type_paiement', '=', 'decaissement')]",
        tracking=True
    )
    
    # Informations communes
    montant = fields.Float(
        string='Montant',
        required=True,
        digits=(16, 2),
        tracking=True
    )
    mode_paiement = fields.Selection(
        [
            ('carte_bancaire', 'Carte bancaire'),
            ('virement', 'Virement bancaire'),
            ('cheque', 'Chèque'),
            ('especes', 'Espèces'),
            ('autre', 'Autre'),
        ],
        string='Mode de paiement',
        required=True,
        tracking=True
    )
    description = fields.Text(
        string='Description',
        tracking=True
    )
    statut = fields.Selection(
        [
            ('en_attente', 'En attente'),
            ('valide', 'Validé'),
            ('annule', 'Annulé'),
        ],
        string='Statut',
        required=True,
        default='valide',
        tracking=True
    )
    
    # Solde de caisse
    solde_avant = fields.Float(
        string='Solde avant',
        compute='_compute_solde',
        store=True,
        digits=(16, 2)
    )
    solde_apres = fields.Float(
        string='Solde après',
        compute='_compute_solde',
        store=True,
        digits=(16, 2)
    )
    
    @api.depends('type_operation', 'montant', 'statut', 'date_operation')
    def _compute_solde(self):
        for record in self:
            # Calculer le solde avant cette opération
            operations_precedentes = self.search([
                ('date_operation', '<=', record.date_operation),
                ('id', '!=', record.id),
                ('statut', '=', 'valide')
            ], order='date_operation, id')
            
            solde_initial = 0.0
            for op in operations_precedentes:
                if op.type_operation == 'encaissement':
                    solde_initial += op.montant
                else:
                    solde_initial -= op.montant
            
            record.solde_avant = solde_initial
            
            # Calculer le solde après cette opération
            if record.statut == 'valide':
                if record.type_operation == 'encaissement':
                    record.solde_apres = record.solde_avant + record.montant
                else:
                    record.solde_apres = record.solde_avant - record.montant
            else:
                record.solde_apres = record.solde_avant
    
    @api.onchange('paiement_client_id')
    def _onchange_paiement_client_id(self):
        """Remplit automatiquement les informations depuis le paiement client"""
        if self.paiement_client_id:
            self.montant = self.paiement_client_id.montant
            self.mode_paiement = self.paiement_client_id.mode_paiement
            self.type_operation = 'encaissement'
    
    @api.onchange('paiement_fournisseur_id')
    def _onchange_paiement_fournisseur_id(self):
        """Remplit automatiquement les informations depuis le paiement fournisseur"""
        if self.paiement_fournisseur_id:
            self.montant = self.paiement_fournisseur_id.montant
            self.mode_paiement = self.paiement_fournisseur_id.mode_paiement
            self.type_operation = 'decaissement'
    
    @api.model
    def create(self, vals):
        """Génère automatiquement le numéro d'opération"""
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('agencevoyage.caisse') or 'Nouveau'
        return super(Caisse, self).create(vals)

