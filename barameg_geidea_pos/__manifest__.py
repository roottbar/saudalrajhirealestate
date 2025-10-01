# -*- coding: utf-8 -*-
{
    'name': "Geidea Terminal Integration",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Geidea Terminal Integration module",
    'description': "Enhanced Geidea Terminal Integration module for Odoo 18.0 by roottbar",
    'category': "Point Of Sale",
    'author': "Barameg",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'point_of_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_payment_method.xml',
        'views/pos_order.xml',
        'views/pos_payment.xml',
        'views/geidea_terminals.xml',
        'views/assets.xml',
        'actions/geidea_terminals.xml',
        'actions/geidea_terminals.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}