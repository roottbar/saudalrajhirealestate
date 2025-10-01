# -*- coding: utf-8 -*-
{
    'name': "Print Journal Entries Report in Odoo",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Print Journal Entries Report in Odoo module",
    'description': "Enhanced Print Journal Entries Report in Odoo module for Odoo 18.0 by roottbar",
    'category': "Account",
    'author': "roottbar",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'report/report_journal_entries.xml',
        'report/report_journal_entries_view.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}
