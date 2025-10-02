# -*- coding: utf-8 -*-
{
    'name': "Approvals",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Approvals module",
    'description': "Enhanced Approvals module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "Crevisoft Corporate",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/manager_sequence_wizard_view.xml',
        'views/user_action_rule.xml',
        'views/res_users.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}
