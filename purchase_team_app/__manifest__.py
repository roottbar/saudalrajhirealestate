# -*- coding: utf-8 -*-
{
    'name': "Odoo Purchase Team Allocation",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Odoo Purchase Team Allocation module",
    'description': "Enhanced Odoo Purchase Team Allocation module for Odoo 18.0 by roottbar",
    'category': "Purchase",
    'author': "Edge Technologies",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/purchase_team_security.xml',
        'views/purchase_team_views.xml',
        'views/data.xml',
        'views/purchase_customer_views.xml',
        'views/purchase_config_views.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}