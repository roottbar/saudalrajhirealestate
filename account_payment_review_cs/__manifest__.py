# -*- coding: utf-8 -*-
{
    'name': 'Account Payment Review Workflow',
    'summary': 'Adds a review state and buttons to account payments before posting.',
    'version': '15.0.1.0.0',
    'author': 'Othmancs',
    'license': 'LGPL-3',
    'category': 'Accounting/Payments',
    'depends': ['account'],
    'data': [
        'security/security.xml',
        'views/account_payment_views.xml',
    ],
    'installable': True,
}