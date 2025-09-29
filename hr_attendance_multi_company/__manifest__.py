# -*- coding: utf-8 -*-
####################################
# Author: Bashier Elbashier
# Date: 27th February, 2021
####################################

{
    'name': 'HR Attendance Multi-company',
    'version': '15.0.1.0.0',
    'author': 'Bashier Elbashier',
    'maintainer': 'roottbar',
    'category': 'Human Resources',
    'summary': 'HR Attendance Multi Company',
    'depends': ['hr', 'hr_attendance'],
    'data': [
        'views/hr_attendance_views.xml',
        'security/security.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
