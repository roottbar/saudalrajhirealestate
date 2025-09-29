# -*- coding: utf-8 -*-
# Odoo 18.0 Compatible - Updated by roottbar
{
    'name': "Partner Accounting Categories",

    'summary': """
        Partner Accounting Categories""",

    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""
        Partner accounting categories used when created customers or vendors to select payable & receivable accounts
    """,
    'author': "Crevisoft",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",
    'category': 'hidden',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_account_category_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_view.xml'
    ],
}
