# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'K.S.A. - Payroll',
    'author': 'Odoo PS',
    'maintainer': 'roottbar',
    'category': 'Human Resources/Payroll',
    'description': """
        
        
        Enhanced Module
        
        
Kingdom of Saudi Arabia Payroll and End of Service rules.
===========================================================

    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'license': 'OEEL-1',
    'depends': ['hr_payroll'],
    'data': [
        'data/hr_payroll_structure_type_data.xml',
        'data/hr_payroll_structure_data.xml',
        'data/hr_salary_rule_data.xml',
        'views/hr_contract_view.xml',
    ],
}
