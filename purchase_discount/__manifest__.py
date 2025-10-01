# -*- coding: utf-8 -*-
{
    'name': "Purchase order lines with discounts",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Purchase order lines with discounts module",
    'description': "Enhanced Purchase order lines with discounts module for Odoo 18.0 by roottbar",
    'category': "Purchase Management",
    'author': "Tiny, Acysos S.L., Tecnativa, ACSONE SA/NV,GRAP,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'purchase_stock',
    ],
    'data': [
        'views/purchase_discount_view.xml',
        'views/report_purchaseorder.xml',
        'views/product_supplierinfo_view.xml',
        'views/res_partner_view.xml',
        'views/res_config_view.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}