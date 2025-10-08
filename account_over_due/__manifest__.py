# -*- coding: utf-8 -*-
{
    'name': "Account Over Due Report",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Account Over Due Report module",
    'description': "Enhanced Account Over Due Report module for Odoo 18.0 by roottbar",
    'category': "Accounting/Accounting",
    'author': "Crevisoft Corporate",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account_followup',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_over_due_views.xml',
        'views/partner_view.xml',
        'views/report_over_due.xml',
        'views/assets.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_over_due/static/src/scss/account_followup_letter.scss',
            'account_over_due/static/src/js/followup_form_controller.js',
            'account_over_due/static/src/js/followup_form_model.js',
            'account_over_due/static/src/js/followup_form_renderer.js',
            'account_over_due/static/src/js/followup_form_view.js',
        ],
        'web.assets_qweb': [
            'account_over_due/static/src/xml/account_over_due_template.xml',
        ],
    },
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}