# -*- coding: utf-8 -*-
{
    'name': 'Construction Project Management',
    'version': '15.0.1.0.0',
    'summary': 'Manage construction projects with detailed cost tracking',
    'description': """
        This module extends Odoo Project to manage construction projects with:
        - Material tracking
        - Labor cost calculation
        - Equipment usage tracking
        - Detailed cost reports
    """,
    'author': 'Othmancs',
    'website': 'https://www.tbarholding.com',
    'category': 'Construction',
    'depends': ['project', 'hr_timesheet', 'maintenance', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_views.xml',
        'reports/project_reports.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
