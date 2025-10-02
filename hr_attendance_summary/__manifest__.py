# -*- coding: utf-8 -*-
{
    'name': "HR Attendance Summary",
    'version': "18.0.1.0.0",
    'summary': "Enhanced HR Attendance Summary module",
    'description': "Enhanced HR Attendance Summary module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "Mahmoud Abdelaziz",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr_attendance',
        'bstt_hr',
        'hr_payroll',
        'hr_overtime',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/salary_rule.xml',
        'views/late_rule.xml',
        'views/hr_attendance_summary.xml',
        'views/resource_calendar.xml',
        'wizard/update_attendance_summary.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}