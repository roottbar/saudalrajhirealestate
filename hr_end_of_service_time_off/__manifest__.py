# -*- coding: utf-8 -*-
{
    'name': "HR End Of Service Time Off",
    'version': "18.0.1.0.0",
    'summary': "Enhanced HR End Of Service Time Off module",
    'description': "Enhanced HR End Of Service Time Off module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "Crevisoft Corporate",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr_end_of_service',
        'hr_holidays',
        'hr_advanced',
    ],
    'data': [
        'data/salary_rules.xml',
        'views/hr_end_service_views.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}