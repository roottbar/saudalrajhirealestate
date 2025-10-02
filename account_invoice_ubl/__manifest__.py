# -*- coding: utf-8 -*-
{
    'name': "Account Invoice UBL",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Account Invoice UBL module",
    'description': "Enhanced Account Invoice UBL module for Odoo 18.0 by roottbar",
    'category': "Accounting & Finance",
    'author': "Akretion,Onestein,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account_einvoice_generate',
        'account_payment_partner',
        'base_ubl_payment',
        'account_tax_unece',
    ],
    'data': [
        'views/account_move.xml',
        'views/res_config_settings.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}