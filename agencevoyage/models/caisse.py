from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import io
import base64
from datetime import datetime


class Caisse(models.Model):
    _name = 'agencevoyage.caisse'
    _description = 'Caisse'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'date_operation desc, id desc'

    name = fields.Char(
        string='Numéro d\'opération',
        required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('agencevoyage.caisse') or 'Nouveau',
        tracking=True,
        readonly=True
    )
    date_operation = fields.Date(
        string='Date d\'opération',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    type_operation = fields.Selection(
        [
            ('encaissement', 'Encaissement'),
            ('decaissement', 'Décaissement'),
        ],
        string='Type d\'opération',
        required=True,
        default='encaissement',
        tracking=True
    )
    
    # Encaissement
    paiement_client_id = fields.Many2one(
        'agencevoyage.paiement',
        string='Paiement client',
        domain="[('type_paiement', '=', 'encaissement')]",
        tracking=True
    )
    
    # Décaissement
    paiement_fournisseur_id = fields.Many2one(
        'agencevoyage.paiement',
        string='Paiement fournisseur',
        domain="[('type_paiement', '=', 'decaissement')]",
        tracking=True
    )
    
    # Informations communes
    montant = fields.Float(
        string='Montant',
        required=True,
        digits=(16, 2),
        tracking=True
    )
    mode_paiement = fields.Selection(
        [
            ('carte_bancaire', 'Carte bancaire'),
            ('virement', 'Virement bancaire'),
            ('cheque', 'Chèque'),
            ('especes', 'Espèces'),
            ('autre', 'Autre'),
        ],
        string='Mode de paiement',
        required=True,
        tracking=True
    )
    description = fields.Text(
        string='Description',
        tracking=True
    )
    statut = fields.Selection(
        [
            ('en_attente', 'En attente'),
            ('valide', 'Validé'),
            ('annule', 'Annulé'),
        ],
        string='Statut',
        required=True,
        default='valide',
        tracking=True
    )
    
    # Solde de caisse
    solde_avant = fields.Float(
        string='Solde avant',
        compute='_compute_solde',
        store=True,
        digits=(16, 2)
    )
    solde_apres = fields.Float(
        string='Solde après',
        compute='_compute_solde',
        store=True,
        digits=(16, 2)
    )
    solde_actuel = fields.Float(
        string='Solde actuel de la caisse',
        compute='_compute_solde_actuel',
        store=False,
        digits=(16, 2),
        help='Solde total actuel de la caisse (toutes opérations validées)'
    )
    
    _sql_constraints = [
        ('check_montant_positive', 'CHECK(montant > 0)', 
         'Le montant doit être strictement positif!'),
    ]
    
    @api.depends('type_operation', 'montant', 'statut', 'date_operation')
    def _compute_solde(self):
        for record in self:
            if not record.date_operation:
                record.solde_avant = 0.0
                record.solde_apres = 0.0
                continue
                
            # Calculer le solde avant cette opération
            # Construire le domaine de recherche
            domain = [
                ('date_operation', '<=', record.date_operation),
                ('statut', '=', 'valide')
            ]
            
            # Exclure l'enregistrement actuel seulement s'il a un ID réel (pas un NewId)
            if isinstance(record.id, int):
                # Pour les opérations à la même date, exclure celles avec un ID supérieur ou égal
                # Utiliser un domaine OR pour exclure: date < OU (date = ET id <)
                domain = [
                    ('statut', '=', 'valide'),
                    '|',
                    ('date_operation', '<', record.date_operation),
                    '&',
                    ('date_operation', '=', record.date_operation),
                    ('id', '<', record.id)
                ]
            # Pour les nouveaux enregistrements, inclure toutes les opérations à la même date
            # car elles seront triées par ID
            
            # Rechercher les opérations précédentes, triées par date puis ID
            operations_precedentes = self.search(domain, order='date_operation asc, id asc')
            
            solde_initial = 0.0
            for op in operations_precedentes:
                if op.type_operation == 'encaissement':
                    solde_initial += op.montant
                else:
                    solde_initial -= op.montant
            
            record.solde_avant = solde_initial
            
            # Calculer le solde après cette opération
            if record.statut == 'valide':
                if record.type_operation == 'encaissement':
                    record.solde_apres = record.solde_avant + record.montant
                else:
                    record.solde_apres = record.solde_avant - record.montant
            else:
                record.solde_apres = record.solde_avant
    
    @api.model
    def _compute_solde_actuel(self):
        """Calcule le solde actuel total de la caisse"""
        operations_validees = self.search([
            ('statut', '=', 'valide')
        ], order='date_operation asc, id asc')
        
        solde_total = 0.0
        for op in operations_validees:
            if op.type_operation == 'encaissement':
                solde_total += op.montant
            else:
                solde_total -= op.montant
        
        # Assigner à tous les enregistrements dans self
        for record in self:
            record.solde_actuel = solde_total
    
    @api.onchange('paiement_client_id')
    def _onchange_paiement_client_id(self):
        """Remplit automatiquement les informations depuis le paiement client"""
        if self.paiement_client_id:
            # Vérifier si le paiement n'est pas déjà utilisé
            existing = self.search([
                ('paiement_client_id', '=', self.paiement_client_id.id),
                ('id', '!=', self.id if isinstance(self.id, int) else False)
            ])
            if existing:
                return {
                    'warning': {
                        'title': _('Paiement déjà utilisé'),
                        'message': _('Ce paiement est déjà associé à une opération de caisse (%s).') % existing[0].name
                    }
                }
            self.montant = self.paiement_client_id.montant
            self.mode_paiement = self.paiement_client_id.mode_paiement
            self.type_operation = 'encaissement'
    
    @api.onchange('paiement_fournisseur_id')
    def _onchange_paiement_fournisseur_id(self):
        """Remplit automatiquement les informations depuis le paiement fournisseur"""
        if self.paiement_fournisseur_id:
            # Vérifier si le paiement n'est pas déjà utilisé
            existing = self.search([
                ('paiement_fournisseur_id', '=', self.paiement_fournisseur_id.id),
                ('id', '!=', self.id if isinstance(self.id, int) else False)
            ])
            if existing:
                return {
                    'warning': {
                        'title': _('Paiement déjà utilisé'),
                        'message': _('Ce paiement est déjà associé à une opération de caisse (%s).') % existing[0].name
                    }
                }
            self.montant = self.paiement_fournisseur_id.montant
            self.mode_paiement = self.paiement_fournisseur_id.mode_paiement
            self.type_operation = 'decaissement'
    
    @api.constrains('montant')
    def _check_montant_positive(self):
        """Vérifie que le montant est positif"""
        for record in self:
            if record.montant <= 0:
                raise ValidationError(_('Le montant doit être strictement positif.'))
    
    @api.constrains('paiement_client_id', 'paiement_fournisseur_id', 'montant')
    def _check_coherence_paiement(self):
        """Vérifie la cohérence entre le paiement sélectionné et le montant"""
        for record in self:
            if record.type_operation == 'encaissement' and record.paiement_client_id:
                if abs(record.montant - record.paiement_client_id.montant) > 0.01:
                    raise ValidationError(_(
                        'Le montant de l\'opération (%s) ne correspond pas au montant du paiement client (%s).'
                    ) % (record.montant, record.paiement_client_id.montant))
            
            if record.type_operation == 'decaissement' and record.paiement_fournisseur_id:
                if abs(record.montant - record.paiement_fournisseur_id.montant) > 0.01:
                    raise ValidationError(_(
                        'Le montant de l\'opération (%s) ne correspond pas au montant du paiement fournisseur (%s).'
                    ) % (record.montant, record.paiement_fournisseur_id.montant))
    
    @api.constrains('paiement_client_id', 'paiement_fournisseur_id')
    def _check_paiement_unique(self):
        """Vérifie qu'un paiement n'est utilisé qu'une seule fois"""
        for record in self:
            if record.paiement_client_id:
                domain = [('paiement_client_id', '=', record.paiement_client_id.id)]
                if isinstance(record.id, int):
                    domain.append(('id', '!=', record.id))
                existing = self.search(domain)
                if existing:
                    raise ValidationError(_(
                        'Le paiement client %s est déjà utilisé dans l\'opération %s.'
                    ) % (record.paiement_client_id.name, existing[0].name))
            
            if record.paiement_fournisseur_id:
                domain = [('paiement_fournisseur_id', '=', record.paiement_fournisseur_id.id)]
                if isinstance(record.id, int):
                    domain.append(('id', '!=', record.id))
                existing = self.search(domain)
                if existing:
                    raise ValidationError(_(
                        'Le paiement fournisseur %s est déjà utilisé dans l\'opération %s.'
                    ) % (record.paiement_fournisseur_id.name, existing[0].name))
    
    def action_annuler(self):
        """Action pour annuler une opération de caisse"""
        for record in self:
            if record.statut == 'annule':
                raise UserError(_('Cette opération est déjà annulée.'))
            if record.statut == 'valide':
                record.statut = 'annule'
                record.message_post(body=_('Opération annulée par %s') % self.env.user.name)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Opération annulée'),
                        'message': _('L\'opération %s a été annulée avec succès.') % record.name,
                        'type': 'success',
                        'sticky': False,
                    }
                }
        return True
    
    @api.model
    def create(self, vals):
        """Génère automatiquement le numéro d'opération"""
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('agencevoyage.caisse') or 'Nouveau'
        return super(Caisse, self).create(vals)
    
    def action_export_excel(self):
        """Exporte les opérations de caisse en Excel"""
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_('Le module xlsxwriter n\'est pas installé. Veuillez l\'installer avec: pip install xlsxwriter'))
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Caisse')
        
        # En-têtes
        headers = ['Numéro', 'Date', 'Type', 'Montant', 'Mode Paiement', 'Solde Avant', 'Solde Après', 'Statut']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # Données
        for row, record in enumerate(self, start=1):
            worksheet.write(row, 0, record.name or '')
            worksheet.write(row, 1, record.date_operation.strftime('%d/%m/%Y') if record.date_operation else '')
            worksheet.write(row, 2, dict(record._fields['type_operation'].selection).get(record.type_operation, ''))
            worksheet.write(row, 3, record.montant)
            worksheet.write(row, 4, dict(record._fields['mode_paiement'].selection).get(record.mode_paiement, ''))
            worksheet.write(row, 5, record.solde_avant)
            worksheet.write(row, 6, record.solde_apres)
            worksheet.write(row, 7, dict(record._fields['statut'].selection).get(record.statut, ''))
        
        workbook.close()
        output.seek(0)
        
        # Créer l'attachement
        filename = f'caisse_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
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
        """Exporte les opérations de caisse en CSV"""
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # En-têtes
        writer.writerow(['Numéro', 'Date', 'Type', 'Montant', 'Mode Paiement', 'Solde Avant', 'Solde Après', 'Statut'])
        
        # Données
        for record in self:
            writer.writerow([
                record.name or '',
                record.date_operation.strftime('%d/%m/%Y') if record.date_operation else '',
                dict(record._fields['type_operation'].selection).get(record.type_operation, ''),
                record.montant,
                dict(record._fields['mode_paiement'].selection).get(record.mode_paiement, ''),
                record.solde_avant,
                record.solde_apres,
                dict(record._fields['statut'].selection).get(record.statut, ''),
            ])
        
        output.seek(0)
        
        # Créer l'attachement
        filename = f'caisse_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
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
    
    def write(self, vals):
        """Le recalcul des soldes est géré automatiquement par les dépendances @api.depends"""
        return super(Caisse, self).write(vals)


