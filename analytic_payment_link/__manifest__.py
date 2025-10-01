# -*- coding: utf-8 -*-
{
    'name': "ربط المدفوعات بالحسابات التحليلية",
    'version': "18.0.1.0.0",
    'summary': "Enhanced ربط المدفوعات بالحسابات التحليلية module",
    'description': "Enhanced ربط المدفوعات بالحسابات التحليلية module for Odoo 18.0 by roottbar",
    'category': "Accounting",
    'author': "Othmancs",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
        'analytic',
    ],
    'data': [
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}