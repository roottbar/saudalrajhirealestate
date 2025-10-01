# -*- coding: utf-8 -*-
{
    'name': "Stock Picking Invoice Link",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Stock Picking Invoice Link module",
    'description': "Enhanced Stock Picking Invoice Link module for Odoo 18.0 by roottbar",
    'category': "Warehouse Management",
    'author': "Agile Business Group, Tecnativa, BCIM sprl, Softdil S.L, Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'sale_stock',
    ],
    'data': [
        'views/stock_view.xml',
        'views/account_invoice_view.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}