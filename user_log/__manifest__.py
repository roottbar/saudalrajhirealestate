# -*- coding: utf-8 -*-
{
    'name': "User Activity Log",
    'version': "18.0.1.0.0",
    'summary': "Enhanced User Activity Log module",
    'description': "Enhanced User Activity Log module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "Othmancs",
    'maintainer': "roottbar",
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/user_log_views.xml',
        'views/user_log_menu.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}