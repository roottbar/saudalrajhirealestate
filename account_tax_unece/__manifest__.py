# -*- coding: utf-8 -*-
{
    'name': "Account Tax UNECE",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Account Tax UNECE module",
    'description': "Enhanced Account Tax UNECE module for Odoo 18.0 by roottbar",
    'category': "Accounting & Finance",
    'author': "Akretion,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
        'base_unece',
    ],
    'data': [
        'views/account_tax.xml',
        'views/account_tax_template.xml',
        'data/unece_tax_type.xml',
        'data/unece_tax_categ.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}