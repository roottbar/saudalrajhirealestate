# -*- coding: utf-8 -*-
{
    'name': "HR Letter",
    'version': "18.0.1.0.0",
    'summary': "Enhanced HR Letter module",
    'description': "Enhanced HR Letter module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "roottbar",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr',
        'hr_contract',
        'bstt_hr',
    ],
    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'report/hr_letter.xml',
        'views/hr_letter.xml',
        'views/hr_employee.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}