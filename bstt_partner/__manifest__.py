# -*- coding: utf-8 -*-
{
    'name': "Electronic invoice BSTT",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Electronic invoice BSTT module",
    'description': "Enhanced Electronic invoice BSTT module for Odoo 18.0 by roottbar",
    'category': "accounting",
    'author': "BSTT company",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/account_move_view.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}
