# -*- coding: utf-8 -*-
{
    'name': "Cost Center Reports",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Cost Center Reports module",
    'description': "Enhanced Cost Center Reports module for Odoo 18.0 by roottbar",
    'category': "Accounting",
    'author': "Othmancs",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'report',
        'account',
        'analytic',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/cost_center_report_views.xml',
        'reports/cost_center_report.xml',
        'reports/cost_center_report_template.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}