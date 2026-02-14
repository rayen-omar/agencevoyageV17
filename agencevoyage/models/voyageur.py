from odoo import models, fields, api


class Voyageur(models.Model):
    _name = 'agencevoyage.voyageur'
    _description = 'Voyageur'
    _order = 'id'

    reservation_id = fields.Many2one(
        'agencevoyage.reservation',
        string='Réservation',
        required=True,
        ondelete='cascade'
    )
    nom = fields.Char(
        string='Nom',
        required=True
    )
    type_voyageur = fields.Selection(
        [
            ('adulte', 'Adulte'),
            ('enfant', 'Enfant'),
        ],
        string='Type',
        required=True,
        default='adulte'
    )
    age = fields.Integer(
        string='Âge',
        help='Âge du voyageur (pour les enfants)'
    )

