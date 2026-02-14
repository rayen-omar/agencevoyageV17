from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class Achat(models.Model):
    _name = 'agencevoyage.achat'
    _description = 'Achat'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'date_achat desc'

    name = fields.Char(
        string='ID Achat',
        required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('agencevoyage.achat') or 'Nouveau',
        tracking=True,
        readonly=True
    )
    date_achat = fields.Date(
        string='Date d\'achat',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    voyage_id = fields.Many2one(
        'agencevoyage.voyage',
        string='Voyage lié',
        required=True,
        tracking=True
    )
    statut = fields.Selection(
        [
            ('devis', 'Devis'),
            ('commande', 'Commande'),
            ('paye', 'Payé'),
            ('annule', 'Annulé'),
        ],
        string='Statut',
        required=True,
        default='devis',
        tracking=True
    )
    
    # Fournisseur
    fournisseur_id = fields.Many2one(
        'agencevoyage.fournisseur',
        string='Fournisseur',
        tracking=True,
        ondelete='restrict'
    )
    
    # Informations fournisseur (peuvent être remplies automatiquement ou manuellement)
    nom_fournisseur = fields.Char(
        string='Nom',
        tracking=True
    )
    type_fournisseur = fields.Selection(
        [
            ('transport', 'Transport'),
            ('hotel', 'Hôtel'),
            ('restaurant', 'Restaurant'),
            ('guide', 'Guide'),
            ('equipement', 'Équipement'),
            ('autre', 'Autre'),
        ],
        string='Type',
        tracking=True
    )
    contact = fields.Char(
        string='Contact',
        tracking=True
    )
    telephone = fields.Char(
        string='Téléphone',
        tracking=True
    )
    email = fields.Char(
        string='Email',
        tracking=True
    )
    
    active = fields.Boolean(
        string='Actif',
        default=True,
        tracking=True
    )
    
    # Lignes d'achat
    ligne_achat_ids = fields.One2many(
        'agencevoyage.ligne_achat',
        'achat_id',
        string='Lignes d\'achat'
    )
    
    # Montant
    pourcentage_tva = fields.Float(
        string='TVA (%)',
        default=19.0,
        digits=(16, 2),
        tracking=True
    )
    montant_ht = fields.Float(
        string='Montant HT',
        compute='_compute_montants',
        store=True,
        digits=(16, 2)
    )
    montant_tva = fields.Float(
        string='Montant TVA',
        compute='_compute_montants',
        store=True,
        digits=(16, 2)
    )
    montant_ttc = fields.Float(
        string='Montant TTC',
        compute='_compute_montants',
        store=True,
        digits=(16, 2)
    )
    
    @api.depends('ligne_achat_ids.total', 'pourcentage_tva')
    def _compute_montants(self):
        for record in self:
            record.montant_ht = sum(record.ligne_achat_ids.mapped('total'))
            record.montant_tva = record.montant_ht * (record.pourcentage_tva / 100)
            record.montant_ttc = record.montant_ht + record.montant_tva
    
    @api.onchange('fournisseur_id')
    def _onchange_fournisseur_id(self):
        """Remplit automatiquement les champs fournisseur quand on sélectionne un fournisseur"""
        if self.fournisseur_id:
            self.nom_fournisseur = self.fournisseur_id.nom
            self.type_fournisseur = self.fournisseur_id.type_fournisseur
            self.contact = self.fournisseur_id.contact
            self.telephone = self.fournisseur_id.telephone
            self.email = self.fournisseur_id.email
    
    # Paiements fournisseur
    paiement_ids = fields.One2many(
        'agencevoyage.paiement',
        'achat_id',
        string='Paiements',
        domain="[('type_paiement', '=', 'decaissement')]"
    )
    
    # Suivi des paiements
    montant_paye = fields.Float(
        string='Montant payé',
        compute='_compute_montant_paye',
        store=True,
        digits=(16, 2)
    )
    reste_a_payer = fields.Float(
        string='Reste à payer',
        compute='_compute_montant_paye',
        store=True,
        digits=(16, 2)
    )
    
    @api.depends('paiement_ids.montant', 'paiement_ids.statut', 'montant_ttc')
    def _compute_montant_paye(self):
        for record in self:
            montant_paye_total = sum(record.paiement_ids.filtered(
                lambda p: p.statut == 'paye'
            ).mapped('montant'))
            record.montant_paye = montant_paye_total
            record.reste_a_payer = record.montant_ttc - montant_paye_total
    
    def action_valider_devis(self):
        """Passe le statut de devis à commande"""
        for record in self:
            if record.statut != 'devis':
                raise UserError(_('Seuls les devis peuvent être validés en commande.'))
            if not record.ligne_achat_ids:
                raise UserError(_('Veuillez ajouter au moins une ligne d\'achat avant de valider.'))
            record.statut = 'commande'
            record.message_post(body=_('Devis validé en commande par %s') % self.env.user.name)
        return True
    
    def action_valider_paye(self):
        """Passe le statut de commande à payé"""
        for record in self:
            if record.statut != 'commande':
                raise UserError(_('Seules les commandes peuvent être marquées comme payées.'))
            record.statut = 'paye'
            record.message_post(body=_('Commande marquée comme payée par %s') % self.env.user.name)
        return True
    
    def action_annuler(self):
        """Annule l'achat"""
        for record in self:
            if record.statut == 'annule':
                raise UserError(_('Cet achat est déjà annulé.'))
            record.statut = 'annule'
            record.message_post(body=_('Achat annulé par %s') % self.env.user.name)
        return True
    
    def action_generer_bon_commande(self):
        """Génère un bon de commande (pour l'instant, retourne une notification)"""
        for record in self:
            if record.statut not in ['devis', 'commande']:
                raise UserError(_('Seuls les devis et commandes peuvent générer un bon de commande.'))
            # TODO: Implémenter la génération du rapport PDF
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Bon de commande'),
                    'message': _('Le bon de commande pour %s sera généré. (Fonctionnalité à implémenter)') % record.name,
                    'type': 'info',
                    'sticky': False,
                }
            }
    
    @api.constrains('statut', 'ligne_achat_ids')
    def _check_lignes_achat(self):
        """Vérifie qu'il y a des lignes d'achat avant validation"""
        for record in self:
            if record.statut in ['commande', 'paye'] and not record.ligne_achat_ids:
                raise ValidationError(_('Un achat en statut "%s" doit avoir au moins une ligne d\'achat.') % dict(record._fields['statut'].selection)[record.statut])
    
    @api.model
    def create(self, vals):
        """Génère automatiquement le numéro d'achat"""
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('agencevoyage.achat') or 'Nouveau'
        return super(Achat, self).create(vals)

