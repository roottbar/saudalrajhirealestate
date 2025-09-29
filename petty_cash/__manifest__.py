# -*- coding: utf-8 -*-
{
    'name': "Petty Cash",

    'summary': """
        Petty Cash""",

    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""
        Petty Cash
    """,

    'author': "Crevisoft",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['board', 'stock', 'account_accountant', 'project', 'account_check_printing', 'attachment_indexation',
                'accounting_category_partner', 'base_dynamic_reports'],
    'assets': {
        'web.assets_qweb': [
            'petty_cash/static/src/xml/*.xml',
        ],
        'web.assets_common': [
            'petty_cash/static/src/css/style_petty_cash.css',
        ],
        'web.assets_backend': [
            'petty_cash/static/src/js/petty_cash_line_import_action.js',
            'petty_cash/static/src/js/fields/custom_basic_fields.js',
            'petty_cash/static/src/js/dynamic_report_petty_cash_lines.js',
            'petty_cash/static/src/js/dynamic_report_request_feeding.js',
        ],
    },
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',

        'wizard/approved_rejected_request_feeding_view.xml',
        'wizard/approved_cancel_petty_cash_request_view.xml',
        'wizard/petty_cash_request_line_view.xml',
        'wizard/accounts_petty_cash_line_config_view.xml',
        'wizard/products_petty_cash_line_config_view.xml',
        'wizard/analytic_accounts_petty_cash_line_config_view.xml',
        'wizard/partners_petty_cash_line_config_view.xml',
        'wizard/petty_cash_transfer_view.xml',
        'views/dynamic_report_petty_cash_lines.xml',
        'views/dynamic_report_request_feeding.xml',
        'views/partner_view.xml',
        'views/petty_cash_line_view.xml',
        'views/petty_cash_view.xml',
        'views/petty_cash_user_rule_view.xml',
        'views/account_move_view.xml',
        'views/account_payment_view.xml',
        'views/petty_cash_request_feeding_view.xml',
        'views/petty_cash_request_view.xml',
        'views/payment_voucher_view.xml',
        'views/res_partner_account_category_views.xml',
        'views/petty_cash_dashboard_view.xml',
        'views/res_config_view.xml',
        'views/petty_cash_report.xml',
        'views/templates.xml',
        'views/menu_petty_cash.xml',
        'data/data.xml',
        'report/report_petty_cash.xml',
        'report/report_petty_cash_lines.xml',
        'report/request_feeding_report.xml',
        'report/report_payment_voucher.xml',
    ],
}
