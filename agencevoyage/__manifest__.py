{
    'name': 'Agence Voyage',
    'version': '17.0.1.0.0',
    'category': 'Services',
    'summary': 'Gestion des clients pour agence de voyage',
    'description': """
        Module de gestion pour agence de voyage
        =========================================
        Ce module permet de gérer les clients de l'agence de voyage avec :
        - Informations personnelles complètes
        - Coordonnées et adresse
        - Photo du client
        - Interface claire et intuitive
    """,
    'author': 'Agence Voyage',
    'website': '',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'data/ir_sequence_data.xml',
        'views/client_views.xml',
        'views/destination_views.xml',
        'views/voyage_views.xml',
        'views/fournisseur_views.xml',
        'views/achat_views.xml',
        'views/reservation_views.xml',
        'views/paiement_views.xml',
        'views/caisse_views.xml',
        'security/ir.model.access.csv',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
