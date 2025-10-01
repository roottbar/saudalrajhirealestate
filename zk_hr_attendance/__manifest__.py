# -*- coding: utf-8 -*-
{
    'name': "ZKTeco biometric attendance",
    'version': "18.0.1.0.0",
    'summary': "Enhanced ZKTeco biometric attendance module",
    'description': "Enhanced ZKTeco biometric attendance module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "Bashier Elbashier",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr',
        'hr_attendance_multi_company',
        'hr_attendance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_attendance_views.xml',
        'views/zk_machine_att_log_views.xml',
        'data/ir_cron.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}