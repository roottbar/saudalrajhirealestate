# -*- coding: utf-8 -*-
{
        
        This module provides:
        * Resume upload and analysis using ATS (Applicant Tracking System)
        * AI-powered resume evaluation based on job positions
        * Comprehensive scoring and feedback system
        * Job position matching and recommendations
        * Detailed reports and analytics
        
        Features:
        ---------
        * Upload resume files (PDF, DOC, DOCX)
        * Select job positions for targeted analysis
        * AI-based resume scoring and evaluation
        * ATS compatibility checking
        * Skills matching and gap analysis
        * Experience evaluation
        * Education verification
        * Keyword optimization suggestions
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'author': 'Your Company',
    'maintainer': 'roottbar',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'name': "HR Resume ATS Analysis",
    'version': "18.0.1.0.0",
    'summary': "Enhanced HR Resume ATS Analysis module",
    'description': "Enhanced HR Resume ATS Analysis module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "Your Company",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr',
        'hr_recruitment',
        'mail',
        'portal',
        'web',
    ],
    'data': [
        'security/hr_resume_ats_security.xml',
        'security/ir.model.access.csv',
        'data/module_data.xml',
        'views/hr_resume_analysis_views.xml',
        'views/hr_job_position_views.xml',
        'views/res_config_settings_views.xml',
        'views/hr_resume_ats_menus.xml',
        'reports/resume_analysis_report.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}