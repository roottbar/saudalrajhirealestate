# -*- coding: utf-8 -*-
{
    'name': "Dynamic Portal",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Dynamic Portal module",
    'description': "Enhanced Dynamic Portal module for Odoo 18.0 by roottbar",
    'category': "web",
    'author': "Mahmoud Abd-Elaziz",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'portal',
        'calendar',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/template.xml',
        'views/sharing_templates.xml',
        'views/portal.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}