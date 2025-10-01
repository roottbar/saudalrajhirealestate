# -*- coding: utf-8 -*-
{
    'name': "تقرير مراكز التكلفة",
    'version': "18.0.1.0.0",
    'summary': "Enhanced تقرير مراكز التكلفة module",
    'description': """
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
    'depends': [
        'base',
        'account',
        'analytic',
    ],
    'data': [
        'views/analytic_account_report_views.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}