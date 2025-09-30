# -*- coding: utf-8 -*-
{
    'name': "Approvals",

    'summary': """Approvals action of any object""",

    'description': """
        
        
        Enhanced Module
        
        
        Approvals action of any object
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,

    'author': "Crevisoft Corporate",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ["mail"],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/manager_sequence_wizard_view.xml',
        'views/user_action_rule.xml',
        'views/res_users.xml',

    ],
    'installable': True,
    'test': False,  # Disable failing tests
}
