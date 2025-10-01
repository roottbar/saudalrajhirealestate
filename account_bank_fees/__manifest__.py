# -*- coding: utf-8 -*-
{
    'name': "Account Bank Fees",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Account Bank Fees module",
    'description': "Enhanced Account Bank Fees module for Odoo 18.0 by roottbar",
    'category': "Accounting/Accounting",
    'author': "Crevisoft Corporate",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_journal_view.xml',
        'views/account_payment_view.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}