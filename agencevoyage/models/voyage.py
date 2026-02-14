from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Voyage(models.Model):
    _name = 'agencevoyage.voyage'
    _description = 'Voyage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'titre_voyage'
    _order = 'date_debut desc'

    # Informations générales
    titre_voyage = fields.Char(
        string='Titre du voyage',
        required=True,
        tracking=True,
        help='Titre du voyage'
    )
    destination_id = fields.Many2one(
        'agencevoyage.destination',
        string='Destination',
        required=True,
        tracking=True,
        help='Destination du voyage'
    )
    ville_depart = fields.Char(
        string='Ville de départ',
        required=True,
        tracking=True
    )
    
    # Dates
    date_debut = fields.Date(
        string='Date de début',
        required=True,
        tracking=True,
        help='Date de début du voyage'
    )
    date_fin = fields.Date(
        string='Date de fin',
        required=True,
        tracking=True,
        help='Date de fin du voyage'
    )
    
    # Prix
    prix_adulte = fields.Float(
        string='Prix adulte',
        required=True,
        digits=(16, 2),
        tracking=True,
        help='Prix pour un adulte'
    )
    prix_enfant = fields.Float(
        string='Prix enfant',
        required=True,
        digits=(16, 2),
        tracking=True,
        help='Prix pour un enfant'
    )
    
    # Places
    place_total = fields.Integer(
        string='Places totales',
        required=True,
        default=1,
        tracking=True,
        help='Nombre total de places disponibles'
    )
    place_reserve = fields.Integer(
        string='Places réservées',
        default=0,
        tracking=True,
        help='Nombre de places déjà réservées'
    )
    
    # Champ calculé pour les places disponibles
    place_disponible = fields.Integer(
        string='Places disponibles',
        compute='_compute_place_disponible',
        store=True,
        help='Nombre de places encore disponibles'
    )
    
    # Photo
    photo = fields.Binary(
        string='Photo',
        attachment=True,
        help='Photo principale du voyage'
    )
    photo_filename = fields.Char(
        string='Nom du fichier photo'
    )
    
    # Relations One2many
    programme_jour_ids = fields.One2many(
        'agencevoyage.programme_jour',
        'voyage_id',
        string='Programme jour par jour'
    )
    transport_ids = fields.One2many(
        'agencevoyage.transport',
        'voyage_id',
        string='Transports'
    )
    hotel_ids = fields.One2many(
        'agencevoyage.hotel',
        'voyage_id',
        string='Hôtels'
    )
    restauration_ids = fields.One2many(
        'agencevoyage.restauration',
        'voyage_id',
        string='Restauration'
    )
    guide_ids = fields.One2many(
        'agencevoyage.guide',
        'voyage_id',
        string='Guides'
    )
    equipement_ids = fields.One2many(
        'agencevoyage.equipement',
        'voyage_id',
        string='Équipements'
    )
    
    @api.depends('place_total', 'place_reserve')
    def _compute_place_disponible(self):
        for record in self:
            record.place_disponible = record.place_total - record.place_reserve
    
    # Contraintes
    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for record in self:
            if record.date_fin and record.date_debut:
                if record.date_fin < record.date_debut:
                    raise ValidationError("La date de fin doit être postérieure à la date de début.")
    
    @api.constrains('place_reserve', 'place_total')
    def _check_places(self):
        for record in self:
            if record.place_reserve < 0:
                raise ValidationError("Le nombre de places réservées ne peut pas être négatif.")
            if record.place_reserve > record.place_total:
                raise ValidationError("Le nombre de places réservées ne peut pas dépasser le nombre total de places.")

