# -*- coding: utf-8 -*-
{
    'name': "Access all OUs",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Access all OUs module",
    'description': "Enhanced Access all OUs module for Odoo 18.0 by roottbar",
    'category': "Sales",
    'author': "Ecosoft,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'analytic_operating_unit',
    ],
    'data': [
        'security/analytic_security.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}