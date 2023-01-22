# -*- coding: utf-8 -*-
{
    'name': "BSTT Account Operating Unit Sequence",
    "version" : "15.0.0.1",
    "category" : "Accounting",
    'description': """
       Account Operating Unit Sequence BSTT
    """,
    'author': "BSTT company",
    'email': "info@bstt.com.sa ",
    'website': "https://bstt.com.sa",
    'category': 'Generic',
    'version': '0.1',
    'license': 'AGPL-3',
    'images': ['static/description/logo.png'],
    'depends': ['operating_unit','account'],
    'data': [
        'views/operating_unit_view.xml',
        'views/account_move_view.xml',
    ],
}
