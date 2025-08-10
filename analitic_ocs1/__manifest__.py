{
    'name': 'Payment Rental Integration',
    'version': '15.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Integration between payments and rental orders with analytical accounts',
    'description': '''
        This module extends payment functionality to:
        - Add rental.order selection in payments
        - Auto-populate related invoices from rental order
        - Apply analytical accounts from invoices to payment entries
    ''',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['account', 'sale_renting', 'analytic'],
    'data': [
        'views/account_payment_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}