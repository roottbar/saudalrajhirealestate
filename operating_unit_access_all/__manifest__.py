# -*- coding: utf-8 -*-
{
    'name': "Access all Operating Units",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Access all Operating Units module",
    'description': "Enhanced Access all Operating Units module for Odoo 18.0 by roottbar",
    'category': "Generic",
    'author': "Ecosoft,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'operating_unit',
    ],
    'data': [
        'security/operating_unit_security.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}