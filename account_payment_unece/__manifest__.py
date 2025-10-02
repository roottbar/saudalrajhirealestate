# -*- coding: utf-8 -*-
{
    'name': "Account Payment UNECE",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Account Payment UNECE module",
    'description': "Enhanced Account Payment UNECE module for Odoo 18.0 by roottbar",
    'category': "Accounting & Finance",
    'author': "Akretion,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account_payment_mode',
        'base_unece',
    ],
    'data': [
        'data/unece.xml',
        'data/account_payment_method.xml',
        'views/account_payment_method.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}