# -*- coding: utf-8 -*-
{
    'name': "BSTT Finger Print",
    "version" : "15.0.0.1",
    "category" : "Accounting",
    'description': """
       Database connection details
    """,
    'author': "BSTT company",
    'email': "info@bstt.com.sa ",
    'website': "https://bstt.com.sa",
    'category': 'accounting',
    'version': '18.0.0.1',
    'license': 'AGPL-3',
    'images': ['static/description/logo.png'],
    'depends': ['base','mail', 'hr','resource','hr_payroll','hr_attendance'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/server_configuration_views.xml',
        'views/hr_employee.xml',
        'views/attendance_data.xml',
        'views/resource_views.xml',
        'views/hr_attendance_view.xml',
        'wizard/reinsert_into_hr_attendance.xml',
    ],
}
