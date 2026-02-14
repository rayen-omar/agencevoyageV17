from odoo import models, fields, api


class Equipement(models.Model):
    _name = 'agencevoyage.equipement'
    _description = 'Équipement'
    _order = 'nom_equipement'

    voyage_id = fields.Many2one(
        'agencevoyage.voyage',
        string='Voyage',
        required=True,
        ondelete='cascade'
    )
    nom_equipement = fields.Char(
        string='Nom de l\'équipement',
        required=True
    )
    quantite = fields.Integer(
        string='Quantité',
        required=True,
        default=1
    )
    prix = fields.Float(
        string='Prix',
        digits=(16, 2),
        required=True
    )

