# -*- coding: utf-8 -*-
{
    'name': "Partner Accounting Categories",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Partner Accounting Categories module",
    'description': "Enhanced Partner Accounting Categories module for Odoo 18.0 by roottbar",
    'category': "hidden",
    'author': "Crevisoft",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_account_category_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_view.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}