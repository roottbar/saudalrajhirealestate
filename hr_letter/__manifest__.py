# -*- coding: utf-8 -*-
{
    'name': "HR Letter",

    'summary': """Letter For Employee""",

    'description': """
        
        
        Enhanced Module
        
        
        Letter For Employee
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'category': 'Human Resources',
    'version': '15.0.1.0',
    'depends': ['hr','hr_contract','bstt_hr'],

    # always loaded
    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'report/hr_letter.xml',
        'views/hr_letter.xml',
        'views/hr_employee.xml',
    ]
}
