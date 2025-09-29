# -*- coding: utf-8 -*-
{
    'name': "Account Report Levels",
    'summary': "Adds levels Buttons in the trial balance",
    'description': "Adds levels Buttons in the trial balance",
    'category': 'Accounting',
    'version': '18.0.0',
    'depends': ['account_reports'],
    'data': [
        'views/template.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            # 'bstt_account_report_levels/static/src/xml/levels.xml',
        ],
    },
}
