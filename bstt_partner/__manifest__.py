# -*- coding: utf-8 -*-
{
    'name': "Electronic invoice BSTT",
    "version" : "14.0.0.1",
    "category" : "Accounting",
    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""
       Electronic invoice BSTT
    """,
    'author': "BSTT company",
    'maintainer': 'roottbar',
    'email': "info@bstt.com.sa ",
    'website': "https://bstt.com.sa",
    'category': 'accounting',
    'version': '18.0.0.1',
    'license': 'AGPL-3',
    'images': ['static/description/logo.png'],
    'depends': ['base', 'account'],
    'data': [
        'views/account_move_view.xml',
    ],
}
