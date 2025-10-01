# -*- coding: utf-8 -*-
{
    'name': "PDF AI Invoice Processor",
    'version': "18.0.1.0.0",
    'summary': "Enhanced PDF AI Invoice Processor module",
    'description': "Enhanced PDF AI Invoice Processor module for Odoo 18.0 by roottbar",
    'category': "Accounting",
    'author': "Othmancs",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/invoice_view.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}