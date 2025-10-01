# -*- coding: utf-8 -*-
{
    'name': "Biostar 2 Biometric Attendance Integration",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Biostar 2 Biometric Attendance Integration module",
    'description': "Enhanced Biostar 2 Biometric Attendance Integration module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "roottbar",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr_attendance',
        'resource',
    ],
    'data': [
        'views/attendance_logs_views.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/biostar_api.xml',
        'wizard/attendance_report_wizard_view.xml',
        'views/menu.xml',
        'views/hr_views.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}
