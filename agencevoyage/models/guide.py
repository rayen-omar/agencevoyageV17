from odoo import models, fields, api


class Guide(models.Model):
    _name = 'agencevoyage.guide'
    _description = 'Guide'
    _order = 'nom_guide'

    voyage_id = fields.Many2one(
        'agencevoyage.voyage',
        string='Voyage',
        required=True,
        ondelete='cascade'
    )
    nom_guide = fields.Char(
        string='Nom du guide',
        required=True
    )
    telephone = fields.Char(
        string='Téléphone'
    )
    email = fields.Char(
        string='Email'
    )
    langue = fields.Char(
        string='Langue',
        required=True,
        help='Langues parlées par le guide'
    )
    prix = fields.Float(
        string='Prix',
        digits=(16, 2),
        required=True
    )

