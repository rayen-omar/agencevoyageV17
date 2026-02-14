from odoo import models, fields, api


class ProgrammeJour(models.Model):
    _name = 'agencevoyage.programme_jour'
    _description = 'Programme jour par jour'
    _order = 'jour'

    voyage_id = fields.Many2one(
        'agencevoyage.voyage',
        string='Voyage',
        required=True,
        ondelete='cascade'
    )
    jour = fields.Integer(
        string='Jour',
        required=True,
        help='Numéro du jour du voyage'
    )
    destination_id = fields.Many2one(
        'agencevoyage.destination',
        string='Destination',
        required=True
    )
    description = fields.Text(
        string='Description',
        required=True,
        help='Description des activités du jour'
    )

