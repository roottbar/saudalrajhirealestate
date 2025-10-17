# -*- coding: utf-8 -*-
{
    'name': "Analytic Operating Unit",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Analytic Operating Unit module",
    'description': "Enhanced Analytic Operating Unit module for Odoo 18.0 by roottbar",
    'category': "Sales",
    'author': "ForgeFlow, Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'analytic',
        'operating_unit',
    ],
    'data': [
        'security/analytic_account_security.xml',
        'views/analytic_account_view.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}