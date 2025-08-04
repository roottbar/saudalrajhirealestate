{
    'name': 'الحسابات التحليلية في الفواتير وبنود اليومية',
    'version': '15.0.1.0.0',
    'summary': 'إضافة الحسابات التحليلية لبنود الفواتير واليوميات بما في ذلك بنود الإقفال والضرائب',
    'description': """
        هذا الموديول يسمح بإضافة الحسابات التحليلية لجميع بنود الفواتير واليوميات
        بما في ذلك بنود الإقفال والضرائب والمصروفات الأخرى.
        يتم تطبيق الحساب التحليلي عند إنشاء الفاتورة وعند ترحيلها.
    """,
    'author': 'othmancs',
    'website': 'https://www.Tbarholding.com',
    'category': 'Accounting',
    'depends': ['account', 'analytic'],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}