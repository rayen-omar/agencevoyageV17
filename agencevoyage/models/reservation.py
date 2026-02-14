from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Reservation(models.Model):
    _name = 'agencevoyage.reservation'
    _description = 'Réservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'date_reservation desc'

    name = fields.Char(
        string='Réservation',
        required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('agencevoyage.reservation') or 'Nouveau',
        tracking=True,
        readonly=True
    )
    date_reservation = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    statut = fields.Selection(
        [
            ('en_attente', 'En attente'),
            ('confirmee', 'Confirmée'),
            ('annulee', 'Annulée'),
            ('terminee', 'Terminée'),
        ],
        string='Statut',
        required=True,
        default='en_attente',
        tracking=True
    )
    voyage_id = fields.Many2one(
        'agencevoyage.voyage',
        string='Voyage',
        required=True,
        tracking=True
    )
    client_id = fields.Many2one(
        'agencevoyage.client',
        string='Client',
        required=True,
        tracking=True
    )
    
    # Voyageurs
    voyageur_ids = fields.One2many(
        'agencevoyage.voyageur',
        'reservation_id',
        string='Voyageurs'
    )
    nombre_adultes = fields.Integer(
        string='Nombre d\'adultes',
        compute='_compute_nombre_voyageurs',
        store=True
    )
    nombre_enfants = fields.Integer(
        string='Nombre d\'enfants',
        compute='_compute_nombre_voyageurs',
        store=True
    )
    total_personnes = fields.Integer(
        string='Total personnes',
        compute='_compute_nombre_voyageurs',
        store=True
    )
    
    # Chambres
    chambre_ids = fields.One2many(
        'agencevoyage.chambre_reservation',
        'reservation_id',
        string='Chambres'
    )
    
    # Calcul automatique des prix
    prix_transport = fields.Float(
        string='Prix Transport',
        compute='_compute_prix_total',
        store=True,
        digits=(16, 2)
    )
    prix_hotel = fields.Float(
        string='Prix Hôtel',
        compute='_compute_prix_total',
        store=True,
        digits=(16, 2)
    )
    prix_restauration = fields.Float(
        string='Prix Restauration',
        compute='_compute_prix_total',
        store=True,
        digits=(16, 2)
    )
    prix_guide = fields.Float(
        string='Prix Guide',
        compute='_compute_prix_total',
        store=True,
        digits=(16, 2)
    )
    prix_equipement = fields.Float(
        string='Prix Équipement',
        compute='_compute_prix_total',
        store=True,
        digits=(16, 2)
    )
    supplement_chambre = fields.Float(
        string='Supplément chambre',
        digits=(16, 2),
        default=0.0,
        tracking=True
    )
    montant_total = fields.Float(
        string='Total',
        compute='_compute_prix_total',
        store=True,
        digits=(16, 2)
    )
    
    # Email de confirmation
    email_confirme = fields.Boolean(
        string='Confirmation envoyée',
        default=False,
        tracking=True
    )
    
    # Paiements
    paiement_ids = fields.One2many(
        'agencevoyage.paiement',
        'reservation_id',
        string='Paiements',
        domain="[('type_paiement', '=', 'encaissement')]"
    )
    
    @api.depends('voyageur_ids.type_voyageur')
    def _compute_nombre_voyageurs(self):
        for record in self:
            record.nombre_adultes = len(record.voyageur_ids.filtered(lambda v: v.type_voyageur == 'adulte'))
            record.nombre_enfants = len(record.voyageur_ids.filtered(lambda v: v.type_voyageur == 'enfant'))
            record.total_personnes = len(record.voyageur_ids)
    
    @api.depends('voyage_id', 'voyageur_ids', 'chambre_ids', 'supplement_chambre')
    def _compute_prix_total(self):
        for record in self:
            if not record.voyage_id or not record.total_personnes:
                record.prix_transport = 0.0
                record.prix_hotel = 0.0
                record.prix_restauration = 0.0
                record.prix_guide = 0.0
                record.prix_equipement = 0.0
                record.montant_total = 0.0
                continue
            
            # Prix transport (basé sur les prix du voyage)
            prix_adulte = record.voyage_id.prix_adulte or 0.0
            prix_enfant = record.voyage_id.prix_enfant or 0.0
            record.prix_transport = (prix_adulte * record.nombre_adultes) + (prix_enfant * record.nombre_enfants)
            
            # Prix hôtel (basé sur les chambres)
            record.prix_hotel = sum(record.chambre_ids.mapped('total_chambre'))
            
            # Prix restauration (basé sur les lignes de restauration du voyage)
            prix_restauration_total = 0.0
            for restauration in record.voyage_id.restauration_ids:
                if restauration.type_repas in ['petit_dejeuner', 'dejeuner']:
                    prix_restauration_total += restauration.prix * record.total_personnes
                elif restauration.type_repas == 'diner':
                    prix_restauration_total += restauration.prix * record.total_personnes
            record.prix_restauration = prix_restauration_total
            
            # Prix guide (basé sur les guides du voyage)
            prix_guide_total = 0.0
            for guide in record.voyage_id.guide_ids:
                prix_guide_total += guide.prix / record.total_personnes if record.total_personnes > 0 else 0
            record.prix_guide = prix_guide_total * record.total_personnes
            
            # Prix équipement (basé sur les équipements du voyage)
            prix_equipement_total = 0.0
            for equipement in record.voyage_id.equipement_ids:
                prix_equipement_total += equipement.prix * record.total_personnes
            record.prix_equipement = prix_equipement_total
            
            # Total
            record.montant_total = (
                record.prix_transport +
                record.prix_hotel +
                record.prix_restauration +
                record.prix_guide +
                record.prix_equipement +
                record.supplement_chambre
            )
    
    @api.model
    def create(self, vals):
        """Génère automatiquement le numéro de réservation"""
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('agencevoyage.reservation') or 'Nouveau'
        return super(Reservation, self).create(vals)

