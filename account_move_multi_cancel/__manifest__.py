# -*- coding: utf-8 -*-
{
    'name': "Mass Journal Entry Cancel",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Mass Journal Entry Cancel module",
    'description': "Enhanced Mass Journal Entry Cancel module for Odoo 18.0 by roottbar",
    'category': "Accounting",
    'author': "Cybrosys Techno Solutions",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/account_move_multi_cancel_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_actions_data.xml',
        'wizards/account_move_cancel_reset_views.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}