# -*- coding: utf-8 -*-
{
    'name': "Accounting Reports Operating",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Accounting Reports Operating module",
    'description': "Enhanced Accounting Reports Operating module for Odoo 18.0 by roottbar",
    'category': "Accounting/Accounting",
    'author': "Crevisoft Corporate",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account_reports',
        'operating_unit',
    ],
    'data': [
        'views/report_financial.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}