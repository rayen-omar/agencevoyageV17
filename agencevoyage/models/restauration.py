from odoo import models, fields, api


class Restauration(models.Model):
    _name = 'agencevoyage.restauration'
    _description = 'Restauration'
    _order = 'jour'

    voyage_id = fields.Many2one(
        'agencevoyage.voyage',
        string='Voyage',
        required=True,
        ondelete='cascade'
    )
    jour = fields.Integer(
        string='Jour',
        required=True
    )
    destination_id = fields.Many2one(
        'agencevoyage.destination',
        string='Destination',
        required=True
    )
    type_repas = fields.Selection(
        [
            ('petit_dejeuner', 'Petit-déjeuner'),
            ('dejeuner', 'Déjeuner'),
            ('diner', 'Dîner'),
            ('collation', 'Collation'),
        ],
        string='Type de repas',
        required=True
    )
    restaurant = fields.Char(
        string='Restaurant',
        required=True
    )
    prix = fields.Float(
        string='Prix',
        digits=(16, 2),
        required=True
    )


