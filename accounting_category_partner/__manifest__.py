# -*- coding: utf-8 -*-
# Odoo 18.0 Compatible - Updated by roottbar
{
    'name': "Partner Accounting Categories",

    'summary': """
        Partner Accounting Categories""",

    'description': """
        
        
        Partner Accounting Categories
        
        Partner accounting categories used when creating customers or vendors 
        to select payable & receivable accounts automatically.
        
        Enhanced by roottbar for Odoo 18.0
    
        
        Enhanced by roottbar.
    """,
    'author': "Crevisoft",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",
    'category': 'hidden',
    'version': '15.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_account_category_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_view.xml'
    ],
}
