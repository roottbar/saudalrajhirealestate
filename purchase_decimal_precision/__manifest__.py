# -*- coding: utf-8 -*-
{
    'name': "Purchase Decimal Precision",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Purchase Decimal Precision module",
    'description': "Enhanced Purchase Decimal Precision module for Odoo 18.0 by roottbar",
    'category': "Purchase",
    'author': "Your Company",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/decimal_precision_data.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}