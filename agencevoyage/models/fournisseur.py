from odoo import models, fields, api


class Fournisseur(models.Model):
    _name = 'agencevoyage.fournisseur'
    _description = 'Fournisseur'
    _rec_name = 'nom'
    _order = 'nom'

    nom = fields.Char(
        string='Nom',
        required=True,
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
        required=True,
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

