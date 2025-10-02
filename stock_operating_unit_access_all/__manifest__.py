# -*- coding: utf-8 -*-
{
    'name': "Access all OUs",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Access all OUs module",
    'description': "Enhanced Access all OUs module for Odoo 18.0 by roottbar",
    'category': "Warehouse Management",
    'author': "Ecosoft,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'stock_operating_unit',
    ],
    'data': [
        'security/stock_security.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}