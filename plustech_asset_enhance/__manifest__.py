# -*- coding: utf-8 -*-
{
    'name': "Accounting Advanced",
    'summary': """  Accounting Advanced""",
    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""  Accounting Asset  """,
    'author': "Plus Tech",
    'maintainer': 'roottbar',
    'category': 'Accounting/Accounting',
    'version': '18.0.0.1',
    'depends': ['account', 'account_asset', 'renting'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/asset.xml',
        'views/account_move.xml',
        'views/sale_rental.xml',
    ],
}
