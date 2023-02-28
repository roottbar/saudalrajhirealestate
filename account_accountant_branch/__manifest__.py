{
    'name': 'Account Accountant Branches',
    'version': '15.0.1.0.0',
    'sequence': 1,
    'depends': ['base_branch', 'account', 'account_branch', 'account_asset', 'account_reports', 'account_accountant'],
    'data': [
        'security/security.xml',
        'views/branch_branch_views.xml',
        'views/account_asset_views.xml',
        'views/res_users_views.xml',
        'views/search_template_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_accountant_branch/static/src/js/custom_account_reports.js',
        ],
    },
    'installable': True,
    'application': True,
}
