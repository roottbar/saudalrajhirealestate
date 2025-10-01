# -*- coding: utf-8 -*-
{
    'name': "Bonus and Deduction",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Bonus and Deduction module",
    'description': "Enhanced Bonus and Deduction module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "Crevisoft Corporate",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr_payroll',
    ],
    'data': [
        'data/data.xml',
        'data/ir_sequence.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_bonus_views.xml',
        'views/hr_deduction_views.xml',
        'views/res_config_views.xml',
        'views/hr_bonus_deduction_menu.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}