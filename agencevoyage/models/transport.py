from odoo import models, fields, api


class Transport(models.Model):
    _name = 'agencevoyage.transport'
    _description = 'Transport'
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
    type_transport = fields.Selection(
        [
            ('avion', 'Avion'),
            ('train', 'Train'),
            ('bus', 'Bus'),
            ('voiture', 'Voiture'),
            ('bateau', 'Bateau'),
            ('autre', 'Autre'),
        ],
        string='Type de transport',
        required=True
    )
    prix = fields.Float(
        string='Prix',
        digits=(16, 2),
        required=True
    )


