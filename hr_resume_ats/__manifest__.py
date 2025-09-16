# -*- coding: utf-8 -*-
{
    'name': 'HR Resume ATS Analysis',
    'version': '15.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Resume Analysis using ATS System with AI Evaluation',
    'description': """
        HR Resume ATS Analysis
        ======================
        
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
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'hr_recruitment',
        'mail',
        'portal',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/job_positions_data.xml',
        'views/hr_resume_analysis_views.xml',
        'views/hr_job_position_views.xml',
        'views/menu_views.xml',
        'reports/resume_analysis_report.xml',
        'reports/resume_analysis_template.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hr_resume_ats/static/src/css/resume_analysis.css',
            'hr_resume_ats/static/src/js/resume_analysis.js',
        ],
        'web.assets_frontend': [
            'hr_resume_ats/static/src/css/portal_resume.css',
        ],
    },
    'external_dependencies': {
        'python': [
            'PyPDF2',
            'python-docx',
            'nltk',
            'textstat',
            'requests',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 95,
}