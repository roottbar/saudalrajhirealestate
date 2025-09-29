# -*- coding: utf-8 -*-
{
    'name': "HR Overtime",

    'summary': """Overtime Requests to employees""",

    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""Overtime Requests to employees""",

    'author': "Mahmoud Abdelaziz",
    'maintainer': 'roottbar',
    'category': 'Human Resources',
    'version': '18.0.0.1',

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
 
