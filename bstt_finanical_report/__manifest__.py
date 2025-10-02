# -*- coding: utf-8 -*-
{
    'name': "BSTT Financial Reports ",
    'version': "18.0.1.0.0",
    'summary': "Enhanced BSTT Financial Reports  module",
    'description': "Enhanced BSTT Financial Reports  module for Odoo 18.0 by roottbar",
    'category': "accounting",
    'author': "BSTT company",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
        'account_reports',
        'renting',
        'account_asset',
    ],
    'data': [
        'views/financial_report.xml',
        'views/account_asset_views.xml',
        'views/account_move_views.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}