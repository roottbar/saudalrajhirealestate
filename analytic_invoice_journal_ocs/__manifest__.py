{
    'name': 'الحساب التحليلي الافتراضي من المنتج',
    'version': '15.0.1.0.1',
    'summary': 'تعيين الحساب التحليلي للمنتج كقيمة افتراضية في بنود الفاتورة',
    'description': """
        يجعل الحساب التحليلي للمنتج هو القيمة الافتراضية في بنود الفاتورة
        مع الحفاظ على إمكانية التعديل يدوياً.
    """,
    'author': 'othmancs',
    'website': 'https://www.TbarHolding.com',
    'category': 'Accounting',
    'depends': ['account', 'analytic', 'sale'],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}