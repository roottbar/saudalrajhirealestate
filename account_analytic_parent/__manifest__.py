# -*- coding: utf-8 -*-
{
    'name': "Account Analytic Parent",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Account Analytic Parent module",
    'description': "Enhanced Account Analytic Parent module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "Matmoz d.o.o., Luxim d.o.o., Deneroteam, ForgeFlow, Tecnativa, CorporateHub, Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
        'analytic',
    ],
    'data': [
        'views/account_analytic_account_view.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}