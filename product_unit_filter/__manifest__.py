# -*- coding: utf-8 -*-
{
    'name': "Product Unit Filter in Sales",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Product Unit Filter in Sales module",
    'description': "Enhanced Product Unit Filter in Sales module for Odoo 18.0 by roottbar",
    'category': "Sales",
    'author': "roottbar",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'sale',
        'product',
    ],
    'data': [
        'views/sale_order_views.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}