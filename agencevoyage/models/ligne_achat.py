from odoo import models, fields, api


class LigneAchat(models.Model):
    _name = 'agencevoyage.ligne_achat'
    _description = 'Ligne d\'achat'
    _order = 'id'

    achat_id = fields.Many2one(
        'agencevoyage.achat',
        string='Achat',
        required=True,
        ondelete='cascade'
    )
    service = fields.Char(
        string='Service',
        required=True
    )
    description = fields.Text(
        string='Description'
    )
    quantite = fields.Float(
        string='Quantité',
        required=True,
        default=1.0,
        digits=(16, 2)
    )
    prix = fields.Float(
        string='Prix unitaire',
        required=True,
        digits=(16, 2)
    )
    total = fields.Float(
        string='Total',
        compute='_compute_total',
        store=True,
        digits=(16, 2)
    )
    
    @api.depends('quantite', 'prix')
    def _compute_total(self):
        for record in self:
            record.total = record.quantite * record.prix


