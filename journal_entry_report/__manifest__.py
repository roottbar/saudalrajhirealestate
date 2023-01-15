# -*- coding: utf-8 -*-
{
    'name': "Journal Entry Report",

    'summary': """
        Journal Entry Report""",

    'description': """
        This module help to print a Journal Entry
    """,

    'author': "Crevisoft Corporate",
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_reports'],

    # always loaded
    'data': [
        'views/account_move_views.xml',
        'views/account_payment_view.xml',
        'views/res_config_view.xml',
        'report/report_journal_entry.xml',
    ],
}
