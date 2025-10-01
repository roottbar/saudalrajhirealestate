# -*- coding: utf-8 -*-
{
    'name': "Date Range",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Date Range module",
    'description': "Enhanced Date Range module for Odoo 18.0 by roottbar",
    'category': "Uncategorized",
    'author': "ACSONE SA/NV, Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'data/ir_cron_data.xml',
        'security/ir.model.access.csv',
        'security/date_range_security.xml',
        'views/date_range_view.xml',
        'wizard/date_range_generator.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}