# -*- coding: utf-8 -*-
# Odoo 18.0 Compatible - Updated by roottbar
{
    'name': "Accounting Advanced",


    'summary': """
        Accounting Advanced""",

    'description': """
        Accounting Advanced Module
        
        This module provides advanced accounting features and enhancements.
        
        Updated for Odoo 18.0 - 2025 Edition
    """,

    'author': "Crevisoft Corporate",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'views/res_config_view.xml',
    ],
}
