# -*- coding: utf-8 -*-
{
    'name': 'Account Archive & Merge',
    'version': '15.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Archive and merge accounts in chart of accounts',
    'description': """
    This module provides:
    * Archive accounts functionality
    * Merge multiple accounts into one
    * Maintain account hierarchy during operations
    * Audit trail for archived and merged accounts
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['account', 'account_parent'],
    'data': [
        'security/ir.model.access.csv',
        'security/account_archive_security.xml',
        'views/account_account_views.xml',
        'wizard/account_merge_wizard_views.xml',
        'wizard/account_archive_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}