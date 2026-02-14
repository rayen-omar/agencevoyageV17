from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Client(models.Model):
    _name = 'agencevoyage.client'
    _description = 'Client de l\'agence de voyage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'nom_complet'
    _order = 'nom, prenom'

    # Informations personnelles
    prenom = fields.Char(
        string='Prénom',
        required=True,
        tracking=True,
        help='Prénom du client'
    )
    nom = fields.Char(
        string='Nom',
        required=True,
        tracking=True,
        help='Nom de famille du client'
    )
    nom_complet = fields.Char(
        string='Nom complet',
        compute='_compute_nom_complet',
        store=True,
        help='Nom complet calculé automatiquement'
    )
    sexe = fields.Selection(
        [
            ('masculin', 'Masculin'),
            ('feminin', 'Féminin'),
        ],
        string='Sexe',
        required=True,
        default='masculin',
        tracking=True
    )
    nationalite = fields.Char(
        string='Nationalité',
        required=True,
        tracking=True,
        help='Nationalité du client'
    )
    
    # Coordonnées
    email = fields.Char(
        string='Email',
        help='Adresse email du client'
    )
    telephone = fields.Char(
        string='Téléphone',
        required=True,
        tracking=True,
        help='Numéro de téléphone du client'
    )
    adresse = fields.Text(
        string='Adresse',
        required=True,
        help='Adresse complète du client'
    )
    
    # Photo
    photo = fields.Binary(
        string='Photo',
        attachment=True,
        help='Photo du client'
    )
    photo_filename = fields.Char(
        string='Nom du fichier photo'
    )
    
    # Documents d'identité
    numero_cin = fields.Char(
        string='Numéro CIN',
        help='Numéro de la carte d\'identité nationale',
        tracking=True
    )
    numero_passport = fields.Char(
        string='Numéro passeport',
        help='Numéro de passeport',
        tracking=True
    )
    
    # Informations bancaires
    numero_bancaire = fields.Char(
        string='Numéro bancaire',
        help='Numéro de compte bancaire',
        tracking=True
    )

    @api.depends('nom', 'prenom')
    def _compute_nom_complet(self):
        """Calcule le nom complet à partir du prénom et du nom"""
        for record in self:
            if record.prenom and record.nom:
                record.nom_complet = f"{record.prenom} {record.nom}".strip()
            elif record.nom:
                record.nom_complet = record.nom
            elif record.prenom:
                record.nom_complet = record.prenom
            else:
                record.nom_complet = ""

    @api.constrains('email')
    def _check_email(self):
        """Valide le format de l'email"""
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError("L'adresse email n'est pas valide. Elle doit contenir le caractère '@'.")

    @api.constrains('telephone')
    def _check_telephone(self):
        """Valide que le téléphone n'est pas vide"""
        for record in self:
            if not record.telephone or not record.telephone.strip():
                raise ValidationError("Le numéro de téléphone est obligatoire.")
