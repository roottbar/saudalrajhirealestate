# -*- coding: utf-8 -*-
{
    'name': "Operating Unit in Products",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Operating Unit in Products module",
    'description': "Enhanced Operating Unit in Products module for Odoo 18.0 by roottbar",
    'category': "Product",
    'author': "brain-tec AG, Open Source Integrators, Serpent Consulting Services Pvt. Ltd.,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'product',
        'operating_unit',
    ],
    'data': [
        'security/product_template_security.xml',
        'views/product_template_view.xml',
        'views/product_category_view.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}