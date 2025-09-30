# -*- coding: utf-8 -*-
{
    'name': "HR Customization BSTT",
    "version": "15.0.0.1",
    "category": "hr",
    'description': """
        
        
        Enhanced Module
        
        
       HR BSTT
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'author': "BSTT company",
    'maintainer': 'roottbar',
    'email': "info@bstt.com.sa ",
    'website': "https://bstt.com.sa",
    'category': 'hr',
    'version': '15.0.1.0',
    'license': 'AGPL-3',
    'images': ['static/description/logo.png'],
    'depends': ['base', 'hr', 'hr_contract', 'project', 'bstt_account_invoice', 'hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'security/security_rules.xml',
        'data/ir_sequence.xml',
        'data/data.xml',
        'data/medical_insurance_type_data.xml',
        # 'data/hr_payroll_data.xml',  # Disabled - requires hr_payroll Enterprise module
        'views/hr.xml',
        'views/hr_department_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_work_location_views.xml',
        'views/hr_start_work_views.xml',
        'views/hr_leave_views.xml',
        'views/hr_travel_views.xml',
        # 'views/hr_payroll.xml',  # Disabled - requires hr_payroll Enterprise module
        'reports/start_work_report_templates.xml',
        # 'wizard/hr_payroll_payslips_by_employees_views.xml',  # Disabled - requires hr_payroll Enterprise module
    ],
}
