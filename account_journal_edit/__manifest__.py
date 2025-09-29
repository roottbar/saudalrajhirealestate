{
    'name': 'تعديل اليومية بعد التأكيد',
    'version': '15.0.1.0.0',
    'category': 'Accounting',
    'summary': 'يسمح بتعديل الحساب في البنود بعد الترحيل',
    'description': """
        
        
        Account Journal Edit Module
        
        هذا الموديول يسمح للمستخدمين المصرح لهم بتعديل الحساب في بنود الفواتير
        بعد تأكيدها دون الحاجة إلى تعديل حالة الفاتورة إلى مسودة.
        
        This module allows authorized users to edit accounts in invoice lines
        after confirmation without changing the invoice state to draft.
        
        Enhanced by roottbar for Odoo 15.0
    
        
        Enhanced by roottbar.
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