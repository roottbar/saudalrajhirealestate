# -*- coding: utf-8 -*-
{
    'name': "Account Report Levels",
    'version': "1.3.9",
    'summary': "Enhanced Account Report Levels module",
    'description': "Enhanced Account Report Levels module for Odoo 18.0 by roottbar",
    'category': "Accounting",
    'author': "roottbar",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account_reports',
    ],
    'data': [
        'views/template.xml',
    ],
    'license': "LGPL-3",
    'installable': True,  # Disabled for Odoo 18 - account_reports.search_template_extra_options no longer exists
    'auto_install': False,
}
