# -*- coding: utf-8 -*-
{
    'name': 'Inventory User Restrict',
    'summary': """Restricts User access to warehouses and Operations""",
    'version': '18.0.1.0.1',
    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""Restricts User access to warehouses and Operations""",
    'author': "Crevisoft",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",
    'category': 'Hidden',
    'depends': ['stock'],
    'data': [
        'security/security.xml',
        'views/res_users_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
