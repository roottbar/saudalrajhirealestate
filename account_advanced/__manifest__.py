# -*- coding: utf-8 -*-
# Odoo 18.0 Compatible - Updated by roottbar
{
    'name': "Accounting Advanced",


    'summary': """
        Accounting Advanced""",

    'description': """
        
        
        Accounting Advanced Module
        
        This module provides advanced accounting features and enhancements.
        
        Enhanced by roottbar for Odoo 15.0
    
        
        Enhanced by roottbar.
    """,

    'author': "Crevisoft Corporate",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '15.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'views/res_config_view.xml',
    ],
}
