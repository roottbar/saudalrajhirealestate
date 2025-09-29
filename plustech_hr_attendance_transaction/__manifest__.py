# -*- coding: utf-8 -*-
{
    'name': "Plus Tech HR Attendance Transaction",
    'version': '15.0.1.0.0',
    'author': 'Plus Technology Team',
    'maintainer': 'roottbar',
    'company': 'Plus Technology',
    'category': 'Human Resources/Attendance',
    'website': "www.plustech-it.com",
    'description': """
        
        
        Enhanced Module
        
        Employees Attendance Transactions Management 
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'summary': """Recording Attendance Transaction for Employees""",
    'depends': ['base',
                'hr',
                'hr_payroll',
                'plustech_hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_attendance_transaction_security.xml',
        'data/data.xml',
        'data/payroll_rule_data.xml',
        'views/hr_attendance_transaction_view.xml',
        'views/exception_request_view.xml',
        'views/hr_payslip.xml',

    ],

    'license': 'OPL-1',
    'demo': [
    ],
}
