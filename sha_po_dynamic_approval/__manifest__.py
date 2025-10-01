# -*- coding: utf-8 -*-
{
    'name': "Dynamic Purchase Order Approval/Purchase Approval",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Dynamic Purchase Order Approval/Purchase Approval module",
    'description': "Enhanced Dynamic Purchase Order Approval/Purchase Approval module for Odoo 18.0 by roottbar",
    'category': "Purchase",
    'author': "Shawon",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/purchase_order_teams_data.xml',
        'views/purchase_order_teams_views.xml',
        'views/purchase_order_view.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}
