# -*- coding: utf-8 -*-
{
    'name': "HR Attendance Summary",

    'summary': """HR Attendance Summary""",

    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""HR Attendance Summary""",

    'author': "Mahmoud Abdelaziz",
    'maintainer': 'roottbar',
    'category': 'Human Resources',
    'version': '18.0.0.1',

    'depends': ['hr_attendance', 'bstt_hr','hr_payroll', 'hr_overtime'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/salary_rule.xml',
        'views/late_rule.xml',
        'views/hr_attendance_summary.xml',
        'views/resource_calendar.xml',
        'wizard/update_attendance_summary.xml',
    ]
}
