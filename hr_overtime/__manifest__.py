# -*- coding: utf-8 -*-
{
    'name': "HR Overtime",

    'summary': """Overtime Requests to employees""",

    'description': """
        
        
        Enhanced Module
        
        Overtime Requests to employees
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,

    'author': "Mahmoud Abdelaziz",
    'maintainer': 'roottbar',
    'category': 'Human Resources',
    'version': '15.0.1.0',
    'installable': False,  # Requires hr_payroll (Enterprise module)

    'depends': ['bstt_hr', 'hr_payroll'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/salary_rule.xml',
        'views/hr_overtime.xml',
        'views/hr_overtime_type.xml',
        'views/res_company_views.xml',
        # 'views/hr_payroll.xml',
    ]
}
 
