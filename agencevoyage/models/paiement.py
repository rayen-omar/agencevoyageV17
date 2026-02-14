from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


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
                domain = [
                    ('reservation_id', '=', record.reservation_id.id),
                    ('statut', '=', 'paye')
                ]
                if isinstance(record.id, int):
                    domain.append(('id', '!=', record.id))
                paiements_existants = self.search(domain)
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
    
    @api.constrains('montant', 'reservation_id', 'type_paiement')
    def _check_montant_coherence(self):
        """Vérifie la cohérence du montant avec la réservation"""
        for record in self:
            if record.type_paiement == 'encaissement' and record.reservation_id:
                if record.montant > record.reste_a_payer + 0.01:  # Tolérance de 0.01 pour les arrondis
                    raise ValidationError(_(
                        'Le montant du paiement (%s) ne peut pas dépasser le reste à payer (%s).'
                    ) % (record.montant, record.reste_a_payer))
    
    @api.constrains('montant')
    def _check_montant_positive(self):
        """Vérifie que le montant est positif"""
        for record in self:
            if record.montant <= 0:
                raise ValidationError(_('Le montant doit être strictement positif.'))
    
    def action_imprimer_recu(self):
        """Action pour imprimer le reçu"""
        for record in self:
            if record.statut != 'paye':
                raise UserError(_('Seuls les paiements payés peuvent être imprimés.'))
            return {
                'type': 'ir.actions.report',
                'report_name': 'agencevoyage.report_paiement',
                'report_type': 'qweb-pdf',
                'res_model': 'agencevoyage.paiement',
                'context': {'active_ids': [record.id]},
            }
    
    @api.model
    def create(self, vals):
        """Génère automatiquement le numéro de paiement et crée l'opération de caisse"""
        if vals.get('name', 'Nouveau') == 'Nouveau':
            if vals.get('type_paiement') == 'encaissement':
                vals['name'] = self.env['ir.sequence'].next_by_code('agencevoyage.paiement.client') or 'Nouveau'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('agencevoyage.paiement.fournisseur') or 'Nouveau'
        
        paiement = super(Paiement, self).create(vals)
        
        # Créer automatiquement une opération de caisse si le paiement est payé
        if paiement.statut == 'paye':
            paiement._create_operation_caisse()
        
        return paiement
    
    def write(self, vals):
        """Crée ou met à jour l'opération de caisse si le statut change"""
        result = super(Paiement, self).write(vals)
        
        # Si le statut change vers 'paye', créer l'opération de caisse
        if 'statut' in vals and vals['statut'] == 'paye':
            for record in self:
                # Vérifier si une opération de caisse existe déjà
                existing_caisse = self.env['agencevoyage.caisse'].search([
                    ('paiement_client_id', '=', record.id) if record.type_paiement == 'encaissement' else ('paiement_fournisseur_id', '=', record.id)
                ])
                if not existing_caisse:
                    record._create_operation_caisse()
        
        return result
    
    def _create_operation_caisse(self):
        """Crée automatiquement une opération de caisse pour ce paiement"""
        for record in self:
            if record.statut != 'paye':
                continue
            
            # Vérifier si une opération de caisse existe déjà
            domain = []
            if record.type_paiement == 'encaissement':
                domain = [('paiement_client_id', '=', record.id)]
            else:
                domain = [('paiement_fournisseur_id', '=', record.id)]
            
            existing = self.env['agencevoyage.caisse'].search(domain)
            if existing:
                continue  # L'opération existe déjà
            
            # Créer l'opération de caisse
            caisse_vals = {
                'date_operation': record.date_paiement,
                'type_operation': 'encaissement' if record.type_paiement == 'encaissement' else 'decaissement',
                'montant': record.montant,
                'mode_paiement': record.mode_paiement,
                'statut': 'valide',
                'description': _('Paiement %s') % record.name,
            }
            
            if record.type_paiement == 'encaissement':
                caisse_vals['paiement_client_id'] = record.id
            else:
                caisse_vals['paiement_fournisseur_id'] = record.id
            
            self.env['agencevoyage.caisse'].create(caisse_vals)

