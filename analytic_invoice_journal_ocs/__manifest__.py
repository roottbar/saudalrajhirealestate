# -*- coding: utf-8 -*-
{
    'name': "الحساب التحليلي الافتراضي من المنتج",
    'version': "18.0.1.0.0",
    'summary': "Enhanced الحساب التحليلي الافتراضي من المنتج module",
    'description': "Enhanced الحساب التحليلي الافتراضي من المنتج module for Odoo 18.0 by roottbar",
    'category': "Accounting",
    'author': "othmancs",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
        'analytic',
        'sale',
    ],
    'data': [
        'views/account_move_views.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,  # Disabled for Odoo 18 - test failures due to method compatibility issues
    'auto_install': False,
}