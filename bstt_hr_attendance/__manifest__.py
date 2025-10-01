# -*- coding: utf-8 -*-
{
    'name': "BSTT HR Attendance ",
    'version': "18.0.1.0.0",
    'summary': "Enhanced BSTT HR Attendance  module",
    'description': "Enhanced BSTT HR Attendance  module for Odoo 18.0 by roottbar",
    'category': "hr",
    'author': "BSTT company",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr_attendance',
    ],
    'data': [
        'security/hr_attendance_security.xml',
        'security/ir.model.access.csv',
        'views/hr_attendance.xml',
        'views/hr_attendance_batch.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}
