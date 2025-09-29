# -*- coding: utf-8 -*-
{
    'name': "BSTT HR Attendance ",
    "version" : "15.0.0.1",
    "category" : "hr",
    'description': """
       Electronic BSTT HR Attendance
    """,
    'author': "BSTT company",
    'email': "info@bstt.com.sa ",
    'website': "https://bstt.com.sa",
    'category': 'hr',
    'version': '18.0.0.1',
    'license': 'AGPL-3',
    'images': ['static/description/logo.png'],
    'depends': ['hr_attendance'],
    'data': [
        'security/hr_attendance_security.xml',
        'security/ir.model.access.csv',
        'views/hr_attendance.xml',
        'views/hr_attendance_batch.xml',

    ],
}
