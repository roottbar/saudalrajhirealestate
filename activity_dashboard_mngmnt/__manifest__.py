# -*- coding: utf-8 -*-
{
    'name': "Activity Management",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Activity Management module",
    'description': "Enhanced Activity Management module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "Cybrosys Techno Solutions",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/my_activity.xml',
        'views/activity_tag.xml',
        'views/activity_dashbord.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}