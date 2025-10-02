{
    'name': 'ربط المدفوعات بالحسابات التحليلية',
    'version': '15.0.1.0.0',
    'summary': 'ربط المدفوعات بحسابات وتحليلات مراكز التكلفة',
    'description': """
        يهدف إلى ربط المدفوعات بحسابات وتحليلات مراكز التكلفة (Analytic Accounts and Tags)،
        مما يُمكن من تتبع التكاليف والإيرادات بشكل أدق من خلال مراكز تحليلية حتى على مستوى الدفع.
    """,
    'author': 'Othmancs',
    'website': 'https://www.Tbarholding.com',
    'category': 'Accounting',
    'depends': ['account', 'analytic'],
    'data': [
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}