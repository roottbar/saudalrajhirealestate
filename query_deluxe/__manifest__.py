{
        'name': 'PostgreSQL Query Deluxe',
        'description': 'Execute postgreSQL query into Odoo interface
        
        Updated for Odoo 18.0 - 2025 Edition',
        'author': 'Yvan Dotet',
    'maintainer': 'roottbar',
        'depends': ['base', 'mail'],
        'application': True,
        'version': '18.0.1.0.0',
        'license': 'AGPL-3',
        'support': 'yvandotet@yahoo.fr',
        'website': 'https://github.com/YvanDotet/',
        'installable': True,

        'data': [
            'security/security.xml',
            'security/ir.model.access.csv',

            'views/query_deluxe_views.xml',

            'wizard/pdforientation.xml',

            'report/print_pdf.xml',

            'datas/data.xml'
            ],

        'images': ['static/description/banner.gif']
}

