# -*- coding: utf-8 -*-


{
    'name': 'Biostar 2 Biometric Attendance Integration',
    'version': '15.0',
    'category': 'Human Resources',
    'sequence': 1,
    'author': '',
    'summary': 'Biometric attendance integration',
    'website': '',
    'license': 'Other proprietary',
    'description': """
 Synchronization of employee attendance with biometric machine ...""",
    'depends': ['hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        #'views/mail_templates.xml',
        'views/biostar_api.xml',
        'views/attendance_logs_views.xml',
        'wizard/attendance_report_wizard_view.xml',
        'views/menu.xml',
    ],
    'demo': [
    ],
    'images': ['images/biostar_2_icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
