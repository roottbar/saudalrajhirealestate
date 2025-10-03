# -*- coding: utf-8 -*-
{
    'name': "K.S.A. - Payroll",
    'version': "18.0.1.0.0",
    'summary': "Enhanced K.S.A. - Payroll module",
    'description': "Enhanced K.S.A. - Payroll module for Odoo 18.0 by roottbar",
    'category': "Human Resources/Payroll",
    'author': "Odoo PS",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr_payroll',
    ],
    'data': [
        'data/hr_payroll_structure_type_data.xml',
        'data/hr_payroll_structure_data.xml',
        'data/hr_salary_rule_data.xml',
        'views/hr_contract_view.xml',
    ],
    'license': "LGPL-3",
    'installable': False,  # Disabled for now - HR modules disabled
    'auto_install': False,
}