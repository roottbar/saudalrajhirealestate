# -*- coding: utf-8 -*-
{
    'name': "Stock Request Picking Type",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Stock Request Picking Type module",
    'description': "Enhanced Stock Request Picking Type module for Odoo 18.0 by roottbar",
    'category': "Warehouse",
    'author': "Open Source Integrators, Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'stock_request',
    ],
    'data': [
        'data/stock_picking_type.xml',
        'views/stock_request_order_views.xml',
        'views/stock_picking_views.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}