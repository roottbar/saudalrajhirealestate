# -*- coding: utf-8 -*-
{
    'name': "Mass Editing",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Mass Editing module",
    'description': "Enhanced Mass Editing module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "Serpent Consulting Services Pvt. Ltd., Tecnativa, Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mass_editing_view.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}