# -*- coding: utf-8 -*-
{
    'name': "Go4whatsup",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Go4whatsup module",
    'description': "Enhanced Go4whatsup module for Odoo 18.0 by roottbar",
    'category': "Extra Tools",
    'author': "Inwizards software Technology Pvt Ltd",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/cron_job.xml',
        'views/views.xml',
        'views/whatsapp.xml',
        'views/res_config.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}