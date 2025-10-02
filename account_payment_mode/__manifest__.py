# -*- coding: utf-8 -*-
{
    'name': "Account Payment Mode",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Account Payment Mode module",
    'description': "Enhanced Account Payment Mode module for Odoo 18.0 by roottbar",
    'category': "Banking addons",
    'author': "Akretion,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/account_payment_mode.xml',
        'security/ir.model.access.csv',
        'views/account_payment_method.xml',
        'views/account_payment_mode.xml',
        'views/account_journal.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}