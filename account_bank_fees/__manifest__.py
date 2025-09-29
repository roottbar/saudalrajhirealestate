# -*- coding: utf-8 -*-
# Odoo 18.0 Compatible - Updated by roottbar
{
    'name': "Account Bank Fees",

    'summary': """
        Account Bank Fees""",


    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""
        Account Bank Fees
    """,

    'author': "Crevisoft Corporate",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_journal_view.xml',
        'views/account_payment_view.xml'
    ],
}
