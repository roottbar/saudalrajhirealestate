# -*- coding: utf-8 -*-
{
    'name': "HR Advanced",

    'summary': """
        HR Advanced""",

    'description': """
        
        
        Enhanced Module
        
        
HR Advanced
===================
It consist of:

# 
1) Allowances 
2) Number and Age Employee
3) Employee Access Own Profile
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,

    'author': "Crevisoft Corporate",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '15.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll','hr_holidays'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/hr_payroll_data.xml',
        'data/medical_insurance_type_data.xml',
        'data/ir_sequence.xml',
        'views/hr_contract_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_medical_insurance_type_view.xml',
        'views/hr_leave_type_views.xml',
        'views/employee_docs.xml',
        'views/employee_docs_expiry.xml',
        'views/request_menu.xml',

    ]
}
