{
    'name': 'تعديل اليومية بعد التأكيد',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'يسمح بتعديل الحساب في البنود بعد الترحيل',
    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""
        هذا الموديول يسمح للمستخدمين المصرح لهم بتعديل الحساب في بنود الفواتير
        بعد تأكيدها دون الحاجة إلى تعديل حالة الفاتورة إلى مسودة.
    """,
    'author': 'Othmancs',
    'maintainer': 'roottbar',
    'website': 'https://www.Tbarholding.com',
    'depends': ['account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}