# -*- coding: utf-8 -*-
{
    'name': "BSTT Account Operating Unit Sequence",
    'version': "18.0.1.0.0",
    'summary': "Enhanced BSTT Account Operating Unit Sequence module",
    'description': "Enhanced BSTT Account Operating Unit Sequence module for Odoo 18.0 by roottbar",
    'category': "Generic",
    'author': "BSTT company",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'operating_unit',
        'account',
        'plustech_asset_enhance',
    ],
    'data': [
        'views/operating_unit_view.xml',
        'views/account_move_view.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}