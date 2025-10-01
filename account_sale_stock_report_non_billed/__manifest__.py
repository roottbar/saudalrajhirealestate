# -*- coding: utf-8 -*-
{
    'name': "Account Sale Stock Report Non Billed",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Account Sale Stock Report Non Billed module",
    'description': "Enhanced Account Sale Stock Report Non Billed module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "Tecnativa, Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'stock_picking_invoice_link',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/stock_move_non_billed_views.xml',
        'security/ir.model.access.csv',
        'wizard/account_sale_stock_report_non_billed_wiz_views.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}