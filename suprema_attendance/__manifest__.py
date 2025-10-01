# -*- coding: utf-8 -*-
{
    'name': "Suprema Biometric Integration",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Suprema Biometric Integration module",
    'description': "Enhanced Suprema Biometric Integration module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "Your Company",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'web',
        'hr',
        'hr_attendance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        'views/device_views.xml',
        'views/attendance_views.xml',
        'views/menu.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}