# -*- coding: utf-8 -*-
{
    'name': "Product Search Multi Value",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Product Search Multi Value module",
    'description': "Enhanced Product Search Multi Value module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'product',
    ],
    'data': [
        'data/search_field_data.xml',
        'views/product_template_view.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}