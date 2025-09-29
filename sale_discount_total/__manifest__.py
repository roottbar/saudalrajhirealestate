# -*- coding: utf-8 -*-
{
    'name': "Sale Discount on Total Amount",

    'summary': """
        Discount on Total in Sale""",

    'description': """
        
        
        Enhanced Module
        
        
        Sale Discount for Total Amount
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,

    'author': "Crevisoft Corporate",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales Management',
    'version': '15.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'views/sales_views.xml'
    ]
}
