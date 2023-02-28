{
    'name': 'Accounting Branches',
    'version': '15.0.1.0.0',
    'sequence': 1,
    'depends': ['base_branch', 'account'],
    'data': [
        'security/security.xml',
        'views/branch_branch_views.xml',
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
        'reports/invoice_report_views.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': True,
}
