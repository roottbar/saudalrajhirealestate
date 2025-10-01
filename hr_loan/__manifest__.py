# -*- coding: utf-8 -*-
{
    'name': "HR Loans",
    'version': "18.0.1.0.0",
    'summary': "Enhanced HR Loans module",
    'description': "Enhanced HR Loans module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "Crevisoft Corporate",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'mail',
        'hr',
        'hr_payroll',
        'hr_payroll_account',
        'bstt_hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_loan_seq.xml',
        'data/salary_rule_loan.xml',
        'views/hr_loan.xml',
        'views/hr_payroll.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}