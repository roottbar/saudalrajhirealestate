# -*- coding: utf-8 -*-
{
    'name': "Purchase Request",

    'summary': """Purchase Request""",

    'description': """
        
        
        Enhanced Module
        
        Create Request for Quotations from Purchase Requests
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,

    'author': "Crevisoft Corporate",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory/Purchase',
    'version': '15.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase_stock', 'user_action_rule', 'hr'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/sequense.xml',
        'data/cron.xml',
        'wizard/purchase_request_quotation_wizard_view.xml',
        'wizard/purchase_request_reject_wizard_view.xml',
        'views/purchase_request.xml',
        'views/purchase_request_line.xml',
        'views/res_config_settings.xml',
        'views/product_category_view.xml',
        'views/menus.xml'
    ]
}
