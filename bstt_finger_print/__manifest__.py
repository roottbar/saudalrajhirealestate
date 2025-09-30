# -*- coding: utf-8 -*-
# Odoo 18.0 Compatible - Migrated by roottbar on 2025-01-30
{
    'name': "BSTT Finger Print",
    "version": "18.0.1.0.0",
    "category" : "Accounting",
    'description': """
        
        
        Enhanced Module
        
        
       Database connection details
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'author': "BSTT company",
    'maintainer': 'roottbar',
    'email': "info@bstt.com.sa ",
    'website': "https://bstt.com.sa",
    'category': 'accounting',
    'version': '18.0.1.0.0',
    'license': 'AGPL-3',
    'images': ['static/description/logo.png'],
    'depends': ['base','mail', 'hr','resource','hr_attendance'],
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
