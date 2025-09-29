# -*- coding: utf-8 -*-
{
    'name': "Plus Tech Employee Custody Management",
    'version': '15.0.1.0.0',  # Updated for 2025 - Force rebuild trigger
    'author': 'Plus Technology Team',
    'company': 'Plus Technology',
    'maintainer': 'roottbar',
    'category': 'Human Resources/Custody',
    'website': "www.plustech-it.com",
    'description': """
        
        
        Employee Custody Management System
        ==================================
        
        This module provides comprehensive custody management for employees including:
        * Asset assignment and tracking
        * Custody requests and approvals
        * Return processes and notifications
        * Integration with HR and Asset modules
        * Automated reminders and reports
        
        Enhanced by roottbar for Odoo 15.0
    
        
        Enhanced by roottbar.
    """,
    'summary': """Complete employee custody and asset management solution""",
    'depends': ['base', 'plustech_hr_employee', 'account_asset'],
    'data': [
        'security/custody_security.xml',
        'security/ir.model.access.csv',
        'data/request_sequance.xml',
        'data/cron.xml',
        'data/template.xml',
        'views/employee_custody.xml',
        'views/custody_items.xml',
        'views/account_asset.xml',
        'views/hr_employee.xml',
    ],
    'demo': [
        # 'demo/custody_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'plustech_hr_employee_custody/static/src/css/custody.css',
            # 'plustech_hr_employee_custody/static/src/js/custody_dashboard.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'price': 0.0,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'application': True,  # Changed to True for better visibility
    'sequence': 10,
}
