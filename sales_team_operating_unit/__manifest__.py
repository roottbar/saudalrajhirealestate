# -*- coding: utf-8 -*-
{
    'name': "Sales Team Operating Unit",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Sales Team Operating Unit module",
    'description': "Enhanced Sales Team Operating Unit module for Odoo 18.0 by roottbar",
    'category': "Sales",
    'author': "ForgeFlow, SerpentCS, Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'sales_team',
        'operating_unit',
    ],
    'data': [
        'security/crm_security.xml',
        'views/crm_team_view.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}