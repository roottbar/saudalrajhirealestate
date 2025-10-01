# -*- coding: utf-8 -*-
{
    'name': "Accounting Advanced",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Accounting Advanced module",
    'description': "Enhanced Accounting Advanced module for Odoo 18.0 by roottbar",
    'category': "Accounting/Accounting",
    'author': "Plus Tech",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
        'account_asset',
        'renting',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/asset.xml',
        'views/account_move.xml',
        'views/sale_rental.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}
