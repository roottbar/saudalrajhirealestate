# -*- coding: utf-8 -*-
{
    'name': "Journal Entry Report",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Journal Entry Report module",
    'description': "Enhanced Journal Entry Report module for Odoo 18.0 by roottbar",
    'category': "Accounting/Accounting",
    'author': "Crevisoft Corporate",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account_reports',
    ],
    'data': [
        'views/account_move_views.xml',
        'views/account_payment_view.xml',
        'views/res_config_view.xml',
        'report/report_journal_entry.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}