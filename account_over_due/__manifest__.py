# -*- coding: utf-8 -*-
{
    'name': 'Account Over Due Report',
    'version': '18.0.1.0',
    'category': 'Accounting/Accounting',
    'description': """Account Over Due Report""",
    'author': "Crevisoft Corporate",
    'website': 'https://www.crevisoft.com',
    'depends': ['account_followup'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_over_due_views.xml',
        'views/partner_view.xml',
        'views/report_over_due.xml',
        'views/assets.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_over_due/static/src/js/followup_form_view.js',
            'account_over_due/static/src/js/followup_form_model.js',
            'account_over_due/static/src/js/followup_form_renderer.js',
            'account_over_due/static/src/js/followup_form_controller.js',
            'account_reports/static/src/scss/account_financial_report.scss',
        ],
        'web.assets_tests': [
            'account_over_due/static/tests/tours/account_reports.js',
        ],
    },
    'qweb': [
        'static/src/xml/account_over_due_template.xml',
    ]
}
