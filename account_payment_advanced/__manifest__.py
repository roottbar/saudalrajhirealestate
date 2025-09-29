# -*- coding: utf-8 -*-
{
    'name': "Account Payment Advanced",

    'summary': """
        Account Payment Advanced""",

    'description': """
        Account Payment Advanced
    """,

    'author': "Crevisoft Corporate",
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
        'views/account_payment_view.xml'
    ],
}
