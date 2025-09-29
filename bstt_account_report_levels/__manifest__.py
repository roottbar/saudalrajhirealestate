# -*- coding: utf-8 -*-
{
    'name': "Account Report Levels",
    'summary': "Adds levels Buttons in the trial balance",
    'description': """Adds levels Buttons in the trial balance
        
        Enhanced by roottbar for better functionality.
    """,
    'category': 'Accounting',
    'version': '15.0.1.0',
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
