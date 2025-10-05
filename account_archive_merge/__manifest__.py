# -*- coding: utf-8 -*-
{
    'name': 'Account Archive & Merge',
    'version': '18.0.1.0.0',
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
    'depends': ['account'],
    'data': [
        'security/account_archive_security.xml',
        'security/ir.model.access.csv',
        'views/account_account_views.xml',
        'views/account_merge_wizard_views.xml',
        'views/account_archive_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}