# -*- coding: utf-8 -*-
{
    'name': "Hr Letter Portal",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Hr Letter Portal module",
    'description': "Enhanced Hr Letter Portal module for Odoo 18.0 by roottbar",
    'category': "hr",
    'author': "BSTT company",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr_letter',
        'dynamic_portal',
    ],
    'data': [
        'data/portal_data.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}