# -*- coding: utf-8 -*-
{
    'name': "Accounting Reports Operating",
    'summary': """Account Reportsl Operating""",
    'author': "Crevisoft Corporate",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",
    'category': 'Accounting/Accounting',
    'version': '18.0.0.1',

    'depends': ['account_reports', 'operating_unit'],

    # always loaded
    'data': [
        # 'wizard/account_report_print_journal_view.xml',
        'views/report_financial.xml'
    ]
}
