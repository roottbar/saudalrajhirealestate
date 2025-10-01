# -*- coding: utf-8 -*-
{
    'name': "Leave Contract Allocation",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Leave Contract Allocation module",
    'description': "Enhanced Leave Contract Allocation module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "Mahmoud Abdelaziz",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr_holidays',
        'hr_contract',
    ],
    'data': [
        'views/hr_leave_type.xml',
        'data/cron.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}