# -*- coding: utf-8 -*-
{
    'name': "Dashboard Ninja",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Dashboard Ninja module",
    'description': "Enhanced Dashboard Ninja module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "Ksolves India Ltd.",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'web',
        'base_setup',
        'bus',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ks_security_groups.xml',
        'data/ks_default_data.xml',
        'views/ks_dashboard_ninja_view.xml',
        'views/ks_dashboard_ninja_item_view.xml',
        'views/ks_dashboard_action.xml',
        'views/ks_import_dashboard_view.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}

