# -*- coding: utf-8 -*-
{
    'name': "Plus Tech HR Attendance Transaction",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Plus Tech HR Attendance Transaction module",
    'description': "Enhanced Plus Tech HR Attendance Transaction module for Odoo 18.0 by roottbar",
    'category': "Human Resources/Attendance",
    'author': "Plus Technology Team",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr',
        'hr_payroll',
        'plustech_hr_attendance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_attendance_transaction_security.xml',
        'data/data.xml',
        'data/payroll_rule_data.xml',
        'views/hr_attendance_transaction_view.xml',
        'views/exception_request_view.xml',
        'views/hr_payslip.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}