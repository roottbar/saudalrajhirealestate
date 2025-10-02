# -*- coding: utf-8 -*-
{
    'name': "Product UoM UNECE",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Product UoM UNECE module",
    'description': "Enhanced Product UoM UNECE module for Odoo 18.0 by roottbar",
    'category': "Sales",
    'author': "Akretion,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'uom',
    ],
    'data': [
        'data/unece.xml',
        'views/uom_uom.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}