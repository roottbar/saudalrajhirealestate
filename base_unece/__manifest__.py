# -*- coding: utf-8 -*-
{
    'name': "Base UNECE",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Base UNECE module",
    'description': "Enhanced Base UNECE module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "Akretion,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
    ],
    'data': [
        'views/unece_code_list.xml',
        'security/ir.model.access.csv',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}