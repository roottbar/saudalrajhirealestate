# -*- coding: utf-8 -*-
{
    'name': "Dashboard Ninja Advance",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Dashboard Ninja Advance module",
    'description': "Enhanced Dashboard Ninja Advance module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "Ksolves India Ltd.",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'ks_dashboard_ninja',
    ],
    'data': [
        'views/ks_dashboard_ninja_item_view_inherit.xml',
        'views/ks_dashboard_form_view_inherit.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}

