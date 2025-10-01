# -*- coding: utf-8 -*-
{
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
        'views/analytic_account_report_views.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}