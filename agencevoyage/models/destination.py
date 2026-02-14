from odoo import models, fields, api


class Destination(models.Model):
    _name = 'agencevoyage.destination'
    _description = 'Destination'
    _rec_name = 'nom_lieu'
    _order = 'nom_lieu'

    # Informations générales
    nom_lieu = fields.Char(
        string='Nom du lieu',
        required=True,
        tracking=True,
        help='Nom du lieu de destination'
    )
    type_destination = fields.Selection(
        [
            ('culturel', 'Culturel'),
            ('religieux', 'Religieux'),
            ('touristique', 'Touristique'),
        ],
        string='Type',
        required=True,
        default='touristique',
        tracking=True
    )
    ville = fields.Char(
        string='Ville',
        required=True,
        tracking=True
    )
    pays = fields.Char(
        string='Pays',
        required=True,
        tracking=True
    )
    
    # Adresse
    adresse = fields.Text(
        string='Adresse',
        required=True,
        help='Adresse complète de la destination'
    )
    
    # Photo
    photo = fields.Binary(
        string='Photo',
        attachment=True,
        help='Photo de la destination'
    )
    photo_filename = fields.Char(
        string='Nom du fichier photo'
    )


