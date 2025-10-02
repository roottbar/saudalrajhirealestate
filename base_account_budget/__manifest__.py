# -*- coding: utf-8 -*-
{
    'name': "Odoo 15 Budget Management",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Odoo 15 Budget Management module",
    'description': "Enhanced Odoo 15 Budget Management module for Odoo 18.0 by roottbar",
    'category': "Accounting",
    'author': "Cybrosys Techno Solutions",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/account_budget_security.xml',
        'views/account_analytic_account_views.xml',
        'views/account_budget_views.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}