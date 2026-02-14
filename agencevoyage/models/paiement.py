from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Paiement(models.Model):
    _name = 'agencevoyage.paiement'
    _description = 'Paiement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'date_paiement desc'

    name = fields.Char(
        string='Numéro de paiement',
        required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('agencevoyage.paiement') or 'Nouveau',
        tracking=True,
        readonly=True
    )
    date_paiement = fields.Date(
        string='Date de paiement',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    type_paiement = fields.Selection(
        [
            ('encaissement', 'Encaissement (Client)'),
            ('decaissement', 'Décaissement (Fournisseur)'),
        ],
        string='Type de paiement',
        required=True,
        default='encaissement',
        tracking=True
    )
    
    # Paiement Client (Encaissement)
    reservation_id = fields.Many2one(
        'agencevoyage.reservation',
        string='Réservation',
        tracking=True
    )
    client_id = fields.Many2one(
        'agencevoyage.client',
        string='Client',
        tracking=True
    )
    type_paiement_client = fields.Selection(
        [
            ('acompte', 'Acompte'),
            ('solde', 'Solde'),
        ],
        string='Type',
        tracking=True
    )
    
    # Paiement Fournisseur (Décaissement)
    fournisseur_id = fields.Many2one(
        'agencevoyage.fournisseur',
        string='Fournisseur',
        tracking=True
    )
    achat_id = fields.Many2one(
        'agencevoyage.achat',
        string='Achat',
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
    reference_bancaire = fields.Char(
        string='Référence bancaire',
        tracking=True
    )
    statut = fields.Selection(
        [
            ('en_attente', 'En attente'),
            ('paye', 'Payé'),
            ('annule', 'Annulé'),
        ],
        string='Statut',
        required=True,
        default='paye',
        tracking=True
    )
    
    # Calculs pour paiement client
    total_a_payer = fields.Float(
        string='Total à payer',
        compute='_compute_montants_client',
        store=True,
        digits=(16, 2)
    )
    deja_paye = fields.Float(
        string='Déjà payé',
        compute='_compute_montants_client',
        store=True,
        digits=(16, 2)
    )
    reste_a_payer = fields.Float(
        string='Reste à payer',
        compute='_compute_montants_client',
        store=True,
        digits=(16, 2)
    )
    
    @api.depends('reservation_id', 'reservation_id.montant_total', 'reservation_id.paiement_ids.montant')
    def _compute_montants_client(self):
        for record in self:
            if record.type_paiement == 'encaissement' and record.reservation_id:
                record.total_a_payer = record.reservation_id.montant_total or 0.0
                # Calculer le total déjà payé (tous les paiements de cette réservation sauf celui en cours)
                paiements_existants = self.search([
                    ('reservation_id', '=', record.reservation_id.id),
                    ('id', '!=', record.id),
                    ('statut', '=', 'paye')
                ])
                record.deja_paye = sum(paiements_existants.mapped('montant'))
                record.reste_a_payer = record.total_a_payer - record.deja_paye - (record.montant if record.statut == 'paye' else 0)
            else:
                record.total_a_payer = 0.0
                record.deja_paye = 0.0
                record.reste_a_payer = 0.0
    
    @api.onchange('reservation_id')
    def _onchange_reservation_id(self):
        """Remplit automatiquement le client quand on sélectionne une réservation"""
        if self.reservation_id:
            self.client_id = self.reservation_id.client_id
    
    @api.onchange('achat_id')
    def _onchange_achat_id(self):
        """Remplit automatiquement le fournisseur quand on sélectionne un achat"""
        if self.achat_id and self.achat_id.fournisseur_id:
            self.fournisseur_id = self.achat_id.fournisseur_id
    
    @api.model
    def create(self, vals):
        """Génère automatiquement le numéro de paiement"""
        if vals.get('name', 'Nouveau') == 'Nouveau':
            if vals.get('type_paiement') == 'encaissement':
                vals['name'] = self.env['ir.sequence'].next_by_code('agencevoyage.paiement.client') or 'Nouveau'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('agencevoyage.paiement.fournisseur') or 'Nouveau'
        return super(Paiement, self).create(vals)

