# -*- coding: utf-8 -*-
{
    'name': "HR Overtime",
    'version': "18.0.1.0.0",
    'summary': "Enhanced HR Overtime module",
    'description': "Enhanced HR Overtime module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "Mahmoud Abdelaziz",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'bstt_hr',
        'hr_payroll',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/salary_rule.xml',
        'views/hr_overtime.xml',
        'views/hr_overtime_type.xml',
        'views/res_company_views.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}