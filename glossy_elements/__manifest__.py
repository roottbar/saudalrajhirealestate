# -*- coding: utf-8 -*-
{
    'name': "Glossy Path Elements",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Glossy Path Elements module",
    'description': "Enhanced Glossy Path Elements module for Odoo 18.0 by roottbar",
    'category': "Uncategorized",
    'author': "O2M Technology",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/elements.xml',
        'views/hr_employee.xml',
        'data/entry_cron.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}