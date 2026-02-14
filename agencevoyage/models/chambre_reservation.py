from odoo import models, fields, api


class ChambreReservation(models.Model):
    _name = 'agencevoyage.chambre_reservation'
    _description = 'Chambre Réservation'
    _order = 'id'

    reservation_id = fields.Many2one(
        'agencevoyage.reservation',
        string='Réservation',
        required=True,
        ondelete='cascade'
    )
    type_chambre = fields.Selection(
        [
            ('simple', 'Chambre simple'),
            ('double', 'Chambre double'),
            ('triple', 'Chambre triple'),
            ('suite', 'Suite'),
        ],
        string='Type de chambre',
        required=True,
        default='double'
    )
    nombre_chambres = fields.Integer(
        string='Nombre de chambres',
        required=True,
        default=1
    )
    nombre_nuits = fields.Integer(
        string='Nombre de nuits',
        required=True,
        default=1
    )
    prix_nuit = fields.Float(
        string='Prix par nuit',
        digits=(16, 2),
        default=0.0
    )
    total_chambre = fields.Float(
        string='Total',
        compute='_compute_total_chambre',
        store=True,
        digits=(16, 2)
    )
    
    @api.depends('nombre_chambres', 'nombre_nuits', 'prix_nuit')
    def _compute_total_chambre(self):
        for record in self:
            record.total_chambre = record.nombre_chambres * record.nombre_nuits * record.prix_nuit

