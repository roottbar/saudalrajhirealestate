# -*- coding: utf-8 -*-
{
    'name': "Invoice Post,Draft and Cancel from List View.",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Invoice Post,Draft and Cancel from List View. module",
    'description': "Enhanced Invoice Post,Draft and Cancel from List View. module for Odoo 18.0 by roottbar",
    'category': "Accounting/Accounting",
    'author': "Naing Lynn Htun",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/account_move.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}