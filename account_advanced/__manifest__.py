# -*- coding: utf-8 -*-
{
    'name': "Accounting Advanced",


    'summary': """
        Accounting Advanced""",

    'description': """
        Accounting Advanced
    """,

    'author': "Crevisoft Corporate",
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
