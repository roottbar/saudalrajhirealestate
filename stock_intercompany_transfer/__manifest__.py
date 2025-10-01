# -*- coding: utf-8 -*-
{
    'name': "Inter Company Stock Transfer",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Inter Company Stock Transfer module",
    'description': "Enhanced Inter Company Stock Transfer module for Odoo 18.0 by roottbar",
    'category': "Warehouse",
    'author': "Cybrosys Techno Solutions",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'stock',
        'account',
    ],
    'data': [
        'views/res_company_view.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}