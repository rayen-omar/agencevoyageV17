from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import io
import base64
from datetime import datetime


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
    
    # Calcul du reste à payer
    deja_paye = fields.Float(
        string='Déjà payé',
        compute='_compute_reste_a_payer',
        store=True,
        digits=(16, 2)
    )
    reste_a_payer = fields.Float(
        string='Reste à payer',
        compute='_compute_reste_a_payer',
        store=True,
        digits=(16, 2)
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
    
    @api.depends('paiement_ids.montant', 'paiement_ids.statut', 'montant_total')
    def _compute_reste_a_payer(self):
        """Calcule le reste à payer pour chaque réservation"""
        for record in self:
            # Calculer le total déjà payé (paiements payés uniquement)
            paiements_payes = record.paiement_ids.filtered(
                lambda p: p.statut == 'paye'
            )
            record.deja_paye = sum(paiements_payes.mapped('montant'))
            record.reste_a_payer = record.montant_total - record.deja_paye
    
    @api.constrains('voyageur_ids', 'voyage_id', 'statut')
    def _check_places_disponibles(self):
        """Vérifie que les places sont disponibles avant confirmation"""
        for record in self:
            if record.statut == 'confirmee' and record.voyage_id:
                places_necessaires = record.total_personnes
                if places_necessaires <= 0:
                    raise ValidationError(_('Veuillez ajouter au moins un voyageur.'))
                
                # Compter les places déjà réservées par d'autres réservations confirmées
                domain = [
                    ('voyage_id', '=', record.voyage_id.id),
                    ('statut', '=', 'confirmee')
                ]
                if isinstance(record.id, int):
                    domain.append(('id', '!=', record.id))
                
                autres_reservations = self.search(domain)
                places_deja_reservees = sum(autres_reservations.mapped('total_personnes'))
                places_disponibles = record.voyage_id.place_total - places_deja_reservees
                
                if places_necessaires > places_disponibles:
                    raise ValidationError(_(
                        'Pas assez de places disponibles. '
                        'Places nécessaires: %d, Places disponibles: %d'
                    ) % (places_necessaires, places_disponibles))
    
    @api.constrains('date_reservation', 'voyage_id')
    def _check_date_reservation(self):
        """Vérifie que la date de réservation est avant le début du voyage"""
        for record in self:
            if record.voyage_id and record.voyage_id.date_debut:
                if record.date_reservation > record.voyage_id.date_debut:
                    raise ValidationError(_(
                        'La date de réservation doit être antérieure à la date de début du voyage (%s).'
                    ) % record.voyage_id.date_debut)
    
    def action_confirmer(self):
        """Confirme la réservation et met à jour les places du voyage"""
        for record in self:
            if record.statut == 'confirmee':
                raise UserError(_('Cette réservation est déjà confirmée.'))
            if record.statut == 'annulee':
                raise UserError(_('Une réservation annulée ne peut pas être confirmée.'))
            if not record.voyageur_ids:
                raise UserError(_('Veuillez ajouter au moins un voyageur avant de confirmer.'))
            
            # Vérifier les places disponibles
            places_necessaires = record.total_personnes
            domain = [
                ('voyage_id', '=', record.voyage_id.id),
                ('statut', '=', 'confirmee')
            ]
            if isinstance(record.id, int):
                domain.append(('id', '!=', record.id))
            
            autres_reservations = self.search(domain)
            places_deja_reservees = sum(autres_reservations.mapped('total_personnes'))
            places_disponibles = record.voyage_id.place_total - places_deja_reservees
            
            if places_necessaires > places_disponibles:
                raise UserError(_(
                    'Pas assez de places disponibles. '
                    'Places nécessaires: %d, Places disponibles: %d'
                ) % (places_necessaires, places_disponibles))
            
            record.statut = 'confirmee'
            record.message_post(body=_('Réservation confirmée par %s') % self.env.user.name)
            
            # Envoyer email de confirmation
            if record.client_id.email:
                template = self.env.ref('agencevoyage.email_template_reservation_confirmation', False)
                if template:
                    template.send_mail(record.id, force_send=True)
                    record.email_confirme = True
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Réservation confirmée'),
                    'message': _('La réservation %s a été confirmée avec succès.') % record.name,
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    def action_annuler(self):
        """Annule la réservation"""
        for record in self:
            if record.statut == 'annulee':
                raise UserError(_('Cette réservation est déjà annulée.'))
            if record.statut == 'terminee':
                raise UserError(_('Une réservation terminée ne peut pas être annulée.'))
            
            record.statut = 'annulee'
            record.message_post(body=_('Réservation annulée par %s') % self.env.user.name)
            
            # Envoyer email de notification
            if record.client_id.email:
                template = self.env.ref('agencevoyage.email_template_reservation_statut_change', False)
                if template:
                    template.send_mail(record.id, force_send=True)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Réservation annulée'),
                    'message': _('La réservation %s a été annulée.') % record.name,
                    'type': 'warning',
                    'sticky': False,
                }
            }
    
    def action_envoyer_rappel_paiement(self):
        """Envoie un email de rappel de paiement au client"""
        for record in self:
            if not record.client_id.email:
                raise UserError(_('Le client n\'a pas d\'adresse email renseignée.'))
            
            if record.reste_a_payer <= 0:
                raise UserError(_('Il n\'y a pas de montant restant à payer pour cette réservation.'))
            
            # Envoyer email de rappel
            template = self.env.ref('agencevoyage.email_template_rappel_paiement', False)
            if template:
                template.send_mail(record.id, force_send=True)
                record.message_post(body=_('Rappel de paiement envoyé par %s') % self.env.user.name)
            else:
                raise UserError(_('Le template d\'email de rappel de paiement n\'a pas été trouvé.'))
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Rappel envoyé'),
                    'message': _('Le rappel de paiement a été envoyé au client %s.') % record.client_id.name,
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    def action_export_excel(self):
        """Exporte les réservations en Excel"""
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_('Le module xlsxwriter n\'est pas installé. Veuillez l\'installer avec: pip install xlsxwriter'))
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Réservations')
        
        # En-têtes
        headers = ['Numéro', 'Date', 'Client', 'Voyage', 'Statut', 'Personnes', 'Montant Total', 'Déjà Payé', 'Reste à Payer']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # Données
        for row, record in enumerate(self, start=1):
            worksheet.write(row, 0, record.name or '')
            worksheet.write(row, 1, record.date_reservation.strftime('%d/%m/%Y') if record.date_reservation else '')
            worksheet.write(row, 2, record.client_id.name if record.client_id else '')
            worksheet.write(row, 3, record.voyage_id.titre_voyage if record.voyage_id else '')
            worksheet.write(row, 4, dict(record._fields['statut'].selection).get(record.statut, ''))
            worksheet.write(row, 5, record.total_personnes)
            worksheet.write(row, 6, record.montant_total)
            worksheet.write(row, 7, record.deja_paye)
            worksheet.write(row, 8, record.reste_a_payer)
        
        workbook.close()
        output.seek(0)
        
        # Créer l'attachement
        filename = f'reservations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
    
    def action_export_csv(self):
        """Exporte les réservations en CSV"""
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # En-têtes
        writer.writerow(['Numéro', 'Date', 'Client', 'Voyage', 'Statut', 'Personnes', 'Montant Total', 'Déjà Payé', 'Reste à Payer'])
        
        # Données
        for record in self:
            writer.writerow([
                record.name or '',
                record.date_reservation.strftime('%d/%m/%Y') if record.date_reservation else '',
                record.client_id.name if record.client_id else '',
                record.voyage_id.titre_voyage if record.voyage_id else '',
                dict(record._fields['statut'].selection).get(record.statut, ''),
                record.total_personnes,
                record.montant_total,
                record.deja_paye,
                record.reste_a_payer,
            ])
        
        output.seek(0)
        
        # Créer l'attachement
        filename = f'reservations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue().encode('utf-8-sig')),
            'mimetype': 'text/csv',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
    
    @api.model
    def create(self, vals):
        """Génère automatiquement le numéro de réservation"""
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('agencevoyage.reservation') or 'Nouveau'
        return super(Reservation, self).create(vals)

