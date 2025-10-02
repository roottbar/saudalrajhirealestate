# -*- coding: utf-8 -*-
{
    'name': 'User Account Restriction',
    'version': '1.0.0',
    'category': 'Accounting',
    'summary': 'Restrict user access to specific accounts in financial screens',
    'description': """
        This module allows administrators to restrict user access to specific accounts
        in all financial screens. Users will not be able to see or access the restricted
        accounts in any financial interface.
        
        Features:
        - Multi-selection dropdown for restricted accounts in user settings
        - Automatic hiding of restricted accounts in all financial screens
        - Security rules to prevent access to restricted accounts
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}