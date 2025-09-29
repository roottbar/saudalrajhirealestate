# -*- coding: utf-8 -*-
{
    'name': "Glossy Path Elements",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        
        
        Enhanced Module
        
        
        Long description of module's purpose
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,

    'author': "O2M Technology",
    'maintainer': 'roottbar',
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/elements.xml',
        'views/hr_employee.xml',
        'data/entry_cron.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
