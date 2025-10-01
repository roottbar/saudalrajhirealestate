# -*- coding: utf-8 -*-
{

        هذا التقرير يقوم بحساب:
        - المصروفات حسب مراكز التكلفة
        - الإيرادات حسب مراكز التكلفة
        - التحصيل حسب مراكز التكلفة
        - المديونية حسب مراكز التكلفة

        مع إمكانية تصدير التقرير إلى Excel أو PDF
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'author': 'othmancs',
    'maintainer': 'roottbar',
    'website': 'https://www.tbarholdingocs.com',
    'category': 'Accounting',
    'depends': ['base', 'account', 'analytic'],
    'name': "تقرير مراكز التكلفة",
    'version': "18.0.1.0.0",
    'summary': "Enhanced تقرير مراكز التكلفة module",
    'description': "Enhanced تقرير مراكز التكلفة module for Odoo 18.0 by roottbar",
    'category': "Accounting",
    'author': "othmancs",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
        'analytic',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/analytic_account_report_views.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}