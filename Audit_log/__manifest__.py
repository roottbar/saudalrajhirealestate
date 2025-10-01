# -*- coding: utf-8 -*-
{
    'name': "Custom Audit Log",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Custom Audit Log module",
    'description': "Enhanced Custom Audit Log module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "Othmancs",
    'maintainer': "roottbar",
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/audit_log_views.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}