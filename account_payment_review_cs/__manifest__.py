{
    'name': 'Vendor Payment Review',
    'summary': 'Adds a review stage to vendor payments before posting.',
    'version': '16.0.1.0.0',
    'author': 'Custom Solutions',
    'depends': ['account', 'petty_cash'],
    'data': [
        'security/security.xml',
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'application': False,
}