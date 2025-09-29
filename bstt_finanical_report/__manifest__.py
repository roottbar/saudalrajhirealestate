# -*- coding: utf-8 -*-
{
    'name': "BSTT Financial Reports ",
    "version" : "15.0.0.1",
    "category" : "Accounting",
    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""
       Electronic Financial Reports BSTT
    """,
    'author': "BSTT company",
    'maintainer': 'roottbar',
    'email': "info@bstt.com.sa ",
    'website': "https://bstt.com.sa",
    'category': 'accounting',
    'version': '18.0.0.1',
    'license': 'AGPL-3',
    'images': ['static/description/logo.png'],
    'depends': ['account', 'account_reports', 'renting', 'account_asset'],
    'data': [
        'views/financial_report.xml',
        'views/account_asset_views.xml',
        'views/account_move_views.xml',
    ],
}
