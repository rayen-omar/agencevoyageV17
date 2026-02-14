from odoo import models, fields, api


class Hotel(models.Model):
    _name = 'agencevoyage.hotel'
    _description = 'Hôtel'
    _order = 'checkin'

    voyage_id = fields.Many2one(
        'agencevoyage.voyage',
        string='Voyage',
        required=True,
        ondelete='cascade'
    )
    destination_id = fields.Many2one(
        'agencevoyage.destination',
        string='Destination',
        required=True
    )
    nom_hotel = fields.Char(
        string='Nom de l\'hôtel',
        required=True
    )
    telephone = fields.Char(
        string='Téléphone'
    )
    adresse = fields.Text(
        string='Adresse',
        required=True
    )
    email = fields.Char(
        string='Email'
    )
    checkin = fields.Date(
        string='Check-in',
        required=True
    )
    checkout = fields.Date(
        string='Check-out',
        required=True
    )
    prix = fields.Float(
        string='Prix',
        digits=(16, 2),
        required=True
    )
    nombre_nuit = fields.Integer(
        string='Nombre de nuits',
        compute='_compute_nombre_nuit',
        store=True
    )
    
    @api.depends('checkin', 'checkout')
    def _compute_nombre_nuit(self):
        for record in self:
            if record.checkin and record.checkout:
                delta = record.checkout - record.checkin
                record.nombre_nuit = delta.days if delta.days > 0 else 0
            else:
                record.nombre_nuit = 0

