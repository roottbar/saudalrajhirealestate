# -*- coding: utf-8 -*-
{
    'name': "Glossy Path Advanced",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Glossy Path Advanced module",
    'description': "Enhanced Glossy Path Advanced module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "Crevisoft Corporate",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account_asset',
        'hr_attendance',
        'hr_payroll',
        'analytic',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_asset_views.xml',
        'views/employee_views.xml',
        'views/hr_payslip_views.xml',
        'views/contract_views.xml',
        'views/res_religion_views.xml',
        'views/hr_job.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}