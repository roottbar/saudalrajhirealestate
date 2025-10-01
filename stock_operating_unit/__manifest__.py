# -*- coding: utf-8 -*-
{
    'name': "Stock with Operating Units",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Stock with Operating Units module",
    'description': "Enhanced Stock with Operating Units module for Odoo 18.0 by roottbar",
    'category': "Generic Modules/Sales & Purchases",
    'author': "ForgeFlow, Serpent Consulting Services Pvt. Ltd., Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'stock',
        'operating_unit',
    ],
    'data': [
        'security/stock_security.xml',
        'data/stock_data.xml',
        'view/stock.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}