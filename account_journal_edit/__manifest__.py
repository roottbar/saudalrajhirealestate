# -*- coding: utf-8 -*-
{
    'name': "تعديل اليومية بعد التأكيد",
    'version': "18.0.1.0.0",
    'summary': "Enhanced تعديل اليومية بعد التأكيد module",
    'description': "Enhanced تعديل اليومية بعد التأكيد module for Odoo 18.0 by roottbar",
    'category': "Accounting",
    'author': "Othmancs",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}