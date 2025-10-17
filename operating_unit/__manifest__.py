# -*- coding: utf-8 -*-
{
    'name': "Operating Units",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Operating Unit module",
    'description': "Enhanced Operating Unit module for Odoo 18.0 by roottbar",
    'category': "Generic",
    'author': "ForgeFlow, Serpent Consulting Services Pvt. Ltd.,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
    ],
    'data': [
        'security/operating_unit_security.xml',
        'security/ir.model.access.csv',
        'data/operating_unit_data.xml',
        'view/operating_unit_view.xml',
        'view/res_users_view.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}
