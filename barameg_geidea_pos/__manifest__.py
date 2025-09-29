# -*- coding: utf-8 -*-
{
    'name': "Geidea Terminal Integration",

    'summary': """
        This module provides integration between, Odoo POS Module and Saudi Geidea POS Terminal without the need to use POSBox.
    """,

    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""
        This module provides integration between, Odoo POS Module and Saudi Geidea POS Terminal without the need to use POSBox.
    """,

    'author': "Barameg",
    'maintainer': 'roottbar',
    'website': "https://barameg.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Point Of Sale',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],
    'images': [
        'static/src/img/1.png',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/pos_payment_method.xml',
        'views/pos_order.xml',
        'views/pos_payment.xml',
        'views/geidea_terminals.xml',
        'views/assets.xml',
        'actions/geidea_terminals.xml',
        'actions/geidea_terminals.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'price': 300.00,
    'currency': 'EUR',

}
