{
    'name': 'الحساب التحليلي الافتراضي من المنتج',
    'version': '18.0.1.0.0',
    'summary': 'تعيين الحساب التحليلي للمنتج كقيمة افتراضية في بنود الفاتورة',
    'description': """
        
        
        Enhanced Module
        
        
        يجعل الحساب التحليلي للمنتج هو القيمة الافتراضية في بنود الفاتورة
        مع الحفاظ على إمكانية التعديل يدوياً.
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'author': 'othmancs',
    'maintainer': 'roottbar',
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