# -*- coding: utf-8 -*-
{
    'name': "HR Loans",

    'summary': """
        Loan Requests to employees""",

    'description': """
        
        
        Enhanced Module
        
        
        Loan Requests to employees
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,

    'author': "Crevisoft Corporate",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '15.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'hr', 'hr_payroll', 'hr_payroll_account', 'bstt_hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_loan_seq.xml',
        'data/salary_rule_loan.xml',
        'views/hr_loan.xml',
        'views/hr_payroll.xml',
        # 'views/res_config_views.xml',
    ]
}
