# -*- coding: utf-8 -*-
{
    'name': "BSTT KSA Ninja Dashboard Add Back Button",
    'version': "18.0.1.0.0",
    'summary': "Enhanced BSTT KSA Ninja Dashboard Add Back Button module",
    'description': "Enhanced BSTT KSA Ninja Dashboard Add Back Button module for Odoo 18.0 by roottbar",
    'category': "Test",
    'author': "BSTT Company",
    'maintainer': "roottbar",
    'depends': [
        'base',
        # 'ks_dashboard_ninja',  # Commented out - module not installable
    ],
    'data': [],
    'qweb': [
        'static/src/xml/bstt_ksa_ninja_dashboard_back_button.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}
