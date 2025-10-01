# -*- coding: utf-8 -*-
{
    'name': "Inventory User Restrict",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Inventory User Restrict module",
    'description': "Enhanced Inventory User Restrict module for Odoo 18.0 by roottbar",
    'category': "Hidden",
    'author': "Crevisoft",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'views/res_users_views.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}