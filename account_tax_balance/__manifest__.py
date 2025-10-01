# -*- coding: utf-8 -*-
{
    'name': "Tax Balance",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Tax Balance module",
    'description': "Enhanced Tax Balance module for Odoo 18.0 by roottbar",
    'category': "Invoices & Payments",
    'author': "Agile Business Group, Therp BV, Tecnativa, ACSONE SA/NV, Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
        'date_range',
    ],
    'data': [
        'wizard/open_tax_balances_view.xml',
        'views/account_move_view.xml',
        'views/account_tax_view.xml',
        'security/ir.model.access.csv',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}