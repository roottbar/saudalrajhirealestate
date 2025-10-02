# -*- coding: utf-8 -*-
{
    'name': "Accounting Reports Branch",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Accounting Reports Branch module",
    'description': "Enhanced Accounting Reports Branch module for Odoo 18.0 by roottbar",
    'category': "Accounting/Accounting",
    'author': "Crevisoft Corporate",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account_reports',
        'branch',
    ],
    'data': [
        'wizard/account_report_print_journal_view.xml',
        'views/report_financial.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}