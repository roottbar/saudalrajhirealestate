# -*- coding: utf-8 -*-
{
    'name': "Accounting Reports Branch",
    'summary': """Account Reportsl Branch""",
    'author': "Crevisoft Corporate",
    'website': "https://www.crevisoft.com",
    'category': 'Accounting/Accounting',
    'version': '0.1',

    'depends': ['account_reports', 'branch'],

    # always loaded
    'data': [
        'wizard/account_report_print_journal_view.xml',
        'views/report_financial.xml'
    ]
}
