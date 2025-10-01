# -*- coding: utf-8 -*-
{
    'name': "HR Attendance Multi-company",
    'version': "18.0.1.0.0",
    'summary': "Enhanced HR Attendance Multi-company module",
    'description': "Enhanced HR Attendance Multi-company module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "Bashier Elbashier",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr',
        'hr_attendance',
    ],
    'data': [
        'views/hr_attendance_views.xml',
        'security/security.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}