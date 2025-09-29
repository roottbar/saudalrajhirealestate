# -*- coding: utf-8 -*-
{
    'name': "Approvals",

    'summary': """Approvals action of any object""",

    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""
        Approvals action of any object
    """,

    'author': "Crevisoft Corporate",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '18.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ["mail"],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/manager_sequence_wizard_view.xml',
        'views/user_action_rule.xml',
        'views/res_users.xml',

    ],

}
