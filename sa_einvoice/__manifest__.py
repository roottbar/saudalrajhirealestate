# -*- coding: utf-8 -*-
{
    'name': "sa_einvoice",

    'summary': """ Saudi e-Invoicing """,

    'description': """
        
        
        Enhanced Module
        
        
        Saudi e-Invoicing
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,

    'author': "BSTT Company",
    'maintainer': 'roottbar',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'accounting',
    'version': '15.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account','uom','account_invoice_ubl'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        # 'data/uom.types.csv',
        # 'data/tax.types.csv',
        # 'data/tax.sub.types.csv',
        'wizards/elect_inv_reason.xml',
        'views/elect_reaons.xml',
        'views/company.xml',
        'views/partner.xml',
        # 'views/product.xml',
        # 'views/units.xml',
        # 'views/res_config_settings.xml',
        'views/invoice.xml',

    ],

}
