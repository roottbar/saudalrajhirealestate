# -*- coding: utf-8 -*-
{
    'name': "Sale Discount on Total Amount",

    'summary': """
        Discount on Total in Sale""",

    'description': """
        Sale Discount for Total Amount
    """,

    'author': "Crevisoft Corporate",
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'views/sales_views.xml'
    ]
}
