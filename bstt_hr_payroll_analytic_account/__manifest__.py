# -*- coding: utf-8 -*-
{
    'name': "BSTT HR Payroll Analytic Account",
    'version': "18.0.1.0.0",
    'summary': "Enhanced BSTT HR Payroll Analytic Account module",
    'description': "Enhanced BSTT HR Payroll Analytic Account module for Odoo 18.0 by roottbar",
    'category': "accounting",
    'author': "BSTT company",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr_payroll_account',
    ],
    'data': [
        'views/hr_payroll_analytic_account_view.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}
