# -*- coding: utf-8 -*-
{
    'name': "Glossy Path Advanced",

    'summary': """
        Glossy Path Advanced""",

    'description': """
        
        
        Enhanced Module
        
        
Glossy Path Advanced
===================
It consist of:

1) Assets 
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,

    'author': "Crevisoft Corporate",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",

    'category': 'Human Resources',
    'version': '15.0.1.0',

    'depends': ['account_asset', 'hr_attendance','hr_payroll','analytic'],

    # always loaded
    'data': [
        # 'security/security.xml',
        'security/ir.model.access.csv',
         'views/account_asset_views.xml',
         'views/employee_views.xml',
         'views/hr_payslip_views.xml',
         'views/contract_views.xml',
         'views/res_religion_views.xml',
         'views/hr_job.xml',
    ]
}
