# -*- coding: utf-8 -*-
{
    'name': "BSTT HR Payroll Analytic Account",
    "version" : "15.0.0.1",
    "category" : "HR",
    'description': """
       HR Payroll Analytic Account BSTT
    """,
    'author': "BSTT company",
    'email': "info@bstt.com.sa ",
    'website': "https://bstt.com.sa",
    'category': 'accounting',
    'version': '0.1',
    'license': 'AGPL-3',
    'images': ['static/description/logo.png'],
    'depends': ['hr_payroll_account'],
    'data': [
        'views/hr_payroll_analytic_account_view.xml',
    ],
    'installable': True
}
